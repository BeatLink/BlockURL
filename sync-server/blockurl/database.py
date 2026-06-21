import sqlite3
from contextlib import contextmanager
from urllib.parse import urlparse


class Queries:
    """Centralized SQL query repository to keep database logic clean and readable."""
    
    # Table Initialization
    CREATE_URLS_TABLE = """
        CREATE TABLE IF NOT EXISTS urls (
            url TEXT PRIMARY KEY,
            domain TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """
    CREATE_SETTINGS_TABLE = """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, 
            value TEXT
        )
    """
    
    # Migrations & Inspections
    TABLE_INFO = "PRAGMA table_info(urls)"
    ADD_DOMAIN_COLUMN = "ALTER TABLE urls ADD COLUMN domain TEXT"
    ADD_CREATED_AT_COLUMN = "ALTER TABLE urls ADD COLUMN created_at TEXT DEFAULT (datetime('now'))"
    BACKFILL_NULL_CREATED_AT = "UPDATE urls SET created_at = datetime('now') WHERE created_at IS NULL"
    GET_UNMAPPED_DOMAINS = "SELECT url FROM urls WHERE domain IS NULL OR domain = ''"
    UPDATE_DOMAIN_FOR_URL = "UPDATE urls SET domain = ? WHERE url = ?"
    CREATE_INDEX_DOMAIN = "CREATE INDEX IF NOT EXISTS idx_urls_domain ON urls(domain)"
    CREATE_INDEX_CREATED_AT = "CREATE INDEX IF NOT EXISTS idx_urls_created_at ON urls(created_at)"
    
    # Rebuild Default Patch
    GET_TABLE_SQL = "SELECT sql FROM sqlite_master WHERE type='table' AND name='urls'"
    RENAME_TO_OLD = "ALTER TABLE urls RENAME TO urls_old"
    MIGRATE_OLD_DATA = """
        INSERT INTO urls (url, domain, created_at)
        SELECT url, domain, COALESCE(created_at, datetime('now')) FROM urls_old
    """
    DROP_OLD_TABLE = "DROP TABLE urls_old"
    
    # Settings Management
    INIT_SETTING = "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)"
    UPDATE_SETTING = "UPDATE settings SET value = ? WHERE key = ?"
    DELETE_SETTING = "DELETE FROM settings WHERE key = ?"
    SELECT_SETTING = "SELECT value FROM settings WHERE key = ?"
    SELECT_ALL_SETTINGS = "SELECT key, value FROM settings"
    
    # URL Operations
    UPSERT_URLS = """
        INSERT INTO urls (url, domain)
        VALUES (?, ?)
        ON CONFLICT(url) DO UPDATE SET domain = excluded.domain
    """
    SELECT_ALL_URLS = "SELECT url FROM urls"
    SELECT_DOMAINS_WITH_COUNTS = """
        SELECT domain, COUNT(*) as count
        FROM urls
        GROUP BY domain
        ORDER BY count DESC
    """


class DatabaseManager:
    def __init__(self, database_name="blockurl.db", create_tables=False, initialize_settings=False):
        self.database_name = database_name
        self._connection = sqlite3.connect(self.database_name, check_same_thread=False)
        
        # Enables dictionary-like row access (e.g., row['domain'] instead of row[1])
        self._connection.row_factory = sqlite3.Row
        
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA busy_timeout=2000")

        if create_tables:
            self.create_all_tables()
            self.migrate_add_columns()
        if initialize_settings:
            self.init_settings()

    def _get_database_(self):
        return self._connection

    @contextmanager
    def connection(self):
        conn = self._get_database_()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def _execute(self, query, params=None, many=False):
        with self.connection() as database:
            cursor = database.cursor()
            if many:
                cursor.executemany(query, params or [])
            else:
                cursor.execute(query, params or [])

    def _fetch_all(self, query, params=None):
        with self.connection() as database:
            cursor = database.cursor()
            cursor.execute(query, params or [])
            return cursor.fetchall()

    def _fetch_one(self, query, params=None):
        with self.connection() as database:
            cursor = database.cursor()
            cursor.execute(query, params or [])
            return cursor.fetchone()

    def create_all_tables(self):
        self._execute(Queries.CREATE_URLS_TABLE)
        self._execute(Queries.CREATE_SETTINGS_TABLE)

    def migrate_add_columns(self):
        existing_columns = [row["name"] for row in self._fetch_all(Queries.TABLE_INFO)]

        if "domain" not in existing_columns:
            self._execute(Queries.ADD_DOMAIN_COLUMN)

        if "created_at" not in existing_columns:
            self._execute(Queries.ADD_CREATED_AT_COLUMN)
            self._execute(Queries.BACKFILL_NULL_CREATED_AT)

        rows_needing_domain = [row["url"] for row in self._fetch_all(Queries.GET_UNMAPPED_DOMAINS)]
        if rows_needing_domain:
            updates = [(self._extract_domain(url), url) for url in rows_needing_domain]
            self._execute(Queries.UPDATE_DOMAIN_FOR_URL, updates, many=True)

        self._execute(Queries.CREATE_INDEX_DOMAIN)
        self._execute(Queries.CREATE_INDEX_CREATED_AT)

        self._repair_created_at_default()

    def _repair_created_at_default(self):
        table_sql = self._fetch_one(Queries.GET_TABLE_SQL)["sql"]

        if "DEFAULT (datetime('now'))" in table_sql or "DEFAULT (datetime(\"now\"))" in table_sql:
            return  

        self._execute(Queries.RENAME_TO_OLD)
        self._execute(Queries.CREATE_URLS_TABLE)
        self._execute(Queries.MIGRATE_OLD_DATA)
        self._execute(Queries.DROP_OLD_TABLE)
        self._execute(Queries.CREATE_INDEX_DOMAIN)
        self._execute(Queries.CREATE_INDEX_CREATED_AT)

    # Settings Methods -------------------------------------------------------------------------------------------------
    def init_settings(self):
        self.create_setting("blocked_page_heading_text", "Blocked")
        self.create_setting("blocked_page_body_text", "This Page has been blocked by BlockURL")
        self.create_setting("blocked_page_button_text", "Unblock")

    def create_setting(self, key, value):
        self._execute(Queries.INIT_SETTING, [key, value])
        return True

    def set_setting(self, key, value):
        self._execute(Queries.UPDATE_SETTING, [value, key])
        return True

    def delete_setting(self, key):
        self._execute(Queries.DELETE_SETTING, [key])
        return True

    def get_setting(self, key):
        row = self._fetch_one(Queries.SELECT_SETTING, [key])
        return row["value"] if row else None

    def get_all_settings(self):
        return [(row["key"], row["value"]) for row in self._fetch_all(Queries.SELECT_ALL_SETTINGS)]

    # URL Methods ------------------------------------------------------------------------------------------------------
    @staticmethod
    def _extract_domain(url):
        netloc = urlparse(url).netloc
        if not netloc:
            netloc = urlparse(f"//{url}").netloc
        return netloc.lower()

    def set_urls(self, urls):
        if not urls:
            return True
        rows = [(url, self._extract_domain(url)) for url in urls]
        self._execute(Queries.UPSERT_URLS, rows, many=True)
        return True

    def delete_urls(self, urls):
        if not urls:
            return True
        # Dynamic IN filters are kept simple and safe using parameterized list generation
        statement = f"DELETE FROM urls WHERE url IN ({','.join(['?'] * len(urls))})"
        self._execute(statement, tuple(urls))
        return True

    def get_urls_exist(self, urls):
        if not urls:
            return {}
        statement = f"SELECT url FROM urls WHERE url IN ({','.join(['?'] * len(urls))})"
        database_matches = {row["url"] for row in self._fetch_all(statement, tuple(urls))}
        return {url: url in database_matches for url in urls}

    def get_all_urls(self):
        return [row["url"] for row in self._fetch_all(Queries.SELECT_ALL_URLS)]

    def get_urls_sorted(self, order_by="created_at", descending=True, domain=None):
        if order_by not in ("created_at", "domain", "url"):
            raise ValueError(f"Invalid order_by column: {order_by}")

        query = "SELECT url, domain, created_at FROM urls"
        params = []
        if domain:
            query += " WHERE domain = ?"
            params.append(domain)
            
        query += f" ORDER BY {order_by} {'DESC' if descending else 'ASC'}"
        return [(row["url"], row["domain"], row["created_at"]) for row in self._fetch_all(query, params)]

    def get_domains_with_counts(self):
        return [(row["domain"], row["count"]) for row in self._fetch_all(Queries.SELECT_DOMAINS_WITH_COUNTS)]