import sqlite3
from contextlib import contextmanager
from urllib.parse import urlparse


class DatabaseManager:
    # Common Methods ---------------------------------------------------------------------------------------------------
    def __init__(self, database_name="blockurl.db", create_tables=False, initialize_settings=False):
        self.database_name = database_name
        # A single persistent connection for the life of the app, rather
        # than opening (and leaking) a new connection on every call.
        # check_same_thread=False because Flask's dev/prod servers may
        # service requests on different threads; SQLite connections are
        # safe to share across threads as long as access isn't truly
        # concurrent, which our request-per-call pattern satisfies.
        self._connection = sqlite3.connect(self.database_name, check_same_thread=False)
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
        """
        Context manager for database connections.
        Automatically commits changes on success or rolls back on error.
        """
        conn = self._get_database_()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def close(self):
        """Closes the database connection if open."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def create_all_tables(self):
        with self.connection() as database:
            cursor = database.cursor()
            create_table_statements = [
                """CREATE TABLE IF NOT EXISTS urls (
                    url TEXT PRIMARY KEY,
                    domain TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )""",
                """CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"""
            ]
            for statement in create_table_statements:
                cursor.execute(statement)

    def migrate_add_columns(self):
        """
        One-time migration for databases created before domain/created_at
        existed. Safe to call every startup; it's a no-op once columns exist.
        """
        with self.connection() as database:
            cursor = database.cursor()
            cursor.execute("PRAGMA table_info(urls)")
            existing_columns = [row[1] for row in cursor.fetchall()]

            if "domain" not in existing_columns:
                cursor.execute("ALTER TABLE urls ADD COLUMN domain TEXT")

            if "created_at" not in existing_columns:
                cursor.execute("ALTER TABLE urls ADD COLUMN created_at TEXT DEFAULT (datetime('now'))")
                # Existing rows have no real creation date on record. Stamping
                # "now" is the best available approximation, not a true value.
                cursor.execute("UPDATE urls SET created_at = datetime('now') WHERE created_at IS NULL")

        # Backfill domain for any rows that don't have one yet (e.g. rows
        # that existed before the domain column, or were inserted oddly).
        with self.connection() as database:
            cursor = database.cursor()
            cursor.execute("SELECT url FROM urls WHERE domain IS NULL OR domain = ''")
            rows_needing_domain = [row[0] for row in cursor.fetchall()]
            if rows_needing_domain:
                update_statement = "UPDATE urls SET domain = ? WHERE url = ?"
                updates = [(self._extract_domain(url), url) for url in rows_needing_domain]
                cursor.executemany(update_statement, updates)

        with self.connection() as database:
            cursor = database.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_domain ON urls(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_created_at ON urls(created_at)")

        self._repair_created_at_default()

    def _repair_created_at_default(self):
        """
        Fixes databases that already ran an earlier version of this migration,
        which added created_at without a DEFAULT clause. SQLite can't alter a
        column to add a default after the fact, so we rebuild the table.
        Safe and cheap to call every startup: it's a no-op once the default
        is correctly attached.
        """
        with self.connection() as database:
            cursor = database.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='urls'")
            table_sql = cursor.fetchone()[0]

            if "DEFAULT (datetime('now'))" in table_sql or "DEFAULT (datetime(\"now\"))" in table_sql:
                return  # default already attached correctly, nothing to do

            cursor.execute("ALTER TABLE urls RENAME TO urls_old")
            cursor.execute("""
                CREATE TABLE urls (
                    url TEXT PRIMARY KEY,
                    domain TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            cursor.execute("""
                INSERT INTO urls (url, domain, created_at)
                SELECT url, domain, COALESCE(created_at, datetime('now')) FROM urls_old
            """)
            cursor.execute("DROP TABLE urls_old")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_domain ON urls(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_created_at ON urls(created_at)")

    # Settings Methods -------------------------------------------------------------------------------------------------
    def init_settings(self):
        self.create_setting("blocked_page_heading_text", "Blocked")
        self.create_setting("blocked_page_body_text", "This Page has been blocked by BlockURL")
        self.create_setting("blocked_page_button_text", "Unblock")

    def create_setting(self, key, value):
        with self.connection() as database:
            cursor = database.cursor()
            statement = "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)"
            cursor.execute(statement, [key, value])
        return True

    def set_setting(self, key, value):
        with self.connection() as database:
            cursor = database.cursor()
            statement = "UPDATE settings SET key = ?, value = ? WHERE key = ?"
            cursor.execute(statement, [key, value, key])
        return True

    def delete_setting(self, key):
        with self.connection() as database:
            cursor = database.cursor()
            statement = "DELETE FROM settings WHERE key = ?"
            cursor.execute(statement, [key])
        return True

    def get_setting(self, key):
        with self.connection() as database:
            cursor = database.cursor()
            statement = "SELECT value FROM settings WHERE key = ?"
            cursor.execute(statement, [key])
            data = cursor.fetchone()
            if data:
                return data[0]

    def get_all_settings(self):
        with self.connection() as database:
            cursor = database.cursor()
            query = "SELECT key, value FROM settings"
            cursor.execute(query)
            return cursor.fetchall()

    # URL Methods ------------------------------------------------------------------------------------------------------
    @staticmethod
    def _extract_domain(url):
        netloc = urlparse(url).netloc
        # Handles URLs passed without a scheme, e.g. "example.com/path"
        if not netloc:
            netloc = urlparse(f"//{url}").netloc
        return netloc.lower()

    def set_urls(self, urls):
        """
        Insert new URLs (with domain + created_at set automatically) or,
        for URLs that already exist, refresh their domain while leaving
        the original created_at untouched.
        """
        with self.connection() as database:
            cursor = database.cursor()
            rows = [(url, self._extract_domain(url)) for url in urls]
            statement = """
                INSERT INTO urls (url, domain)
                VALUES (?, ?)
                ON CONFLICT(url) DO UPDATE SET domain = excluded.domain
            """
            cursor.executemany(statement, rows)
        return True

    def delete_urls(self, urls):
        with self.connection() as database:
            cursor = database.cursor()
            statement = f"DELETE FROM urls WHERE url IN ({','.join(['?'] * len(urls))})"
            cursor.execute(statement, tuple(urls))
        return True

    def get_urls_exist(self, urls):
        with self.connection() as database:
            cursor = database.cursor()
            statement = f"SELECT url FROM urls WHERE url IN ({','.join(['?'] * len(urls))})"
            cursor.execute(statement, tuple(urls))
            database_matches = cursor.fetchall()
            database_matches = [url[0] for url in database_matches]
            results = {url: url in database_matches for url in urls}
            return results

    def get_all_urls(self):
        with self.connection() as database:
            cursor = database.cursor()
            query = "SELECT url FROM urls"
            cursor.execute(query)
            return [url[0] for url in cursor.fetchall()]

    def get_urls_sorted(self, order_by="created_at", descending=True, domain=None):
        """
        order_by: 'created_at', 'domain', or 'url'
        domain: optional exact-match filter, e.g. 'example.com'
        Returns list of (url, domain, created_at) tuples.
        """
        if order_by not in ("created_at", "domain", "url"):
            raise ValueError(f"Invalid order_by column: {order_by}")

        with self.connection() as database:
            cursor = database.cursor()
            query = "SELECT url, domain, created_at FROM urls"
            params = []
            if domain:
                query += " WHERE domain = ?"
                params.append(domain)
            query += f" ORDER BY {order_by} {'DESC' if descending else 'ASC'}"
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_domains_with_counts(self):
        """Returns list of (domain, count) tuples, most-blocked first."""
        with self.connection() as database:
            cursor = database.cursor()
            query = """
                SELECT domain, COUNT(*) as count
                FROM urls
                GROUP BY domain
                ORDER BY count DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
