import datetime
from datetime import timezone
from urllib.parse import urlparse
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.migrate import SqliteMigrator, migrate

from .matching import match_key

# 1. Initialize an un-deferred database proxy
db = SqliteExtDatabase(None)  # Peewee 3.x uses thread-local connections by default


def in_connection(call, *args, **kwargs):
    """Run a database call with a connection belonging to the calling thread.

    Peewee keeps one connection per thread, and the server hands work to worker
    threads, so the connection has to be opened and closed where the work runs.
    """
    with db.connection_context():
        return call(*args, **kwargs)


# 2. Declarative Models (Bound to the Proxy Database)
class BaseModel(Model):
    class Meta:
        database = db


class URL(BaseModel):
    url = CharField(primary_key=True)
    domain = CharField(null=True, index=True)
    match_key = CharField(null=True, index=True)
    created_at = DateTimeField(default=lambda: datetime.datetime.now(timezone.utc), index=True)


class Setting(BaseModel):
    key = CharField(primary_key=True)
    value = CharField()


def _first_per_key(urls):
    """Keep the first URL for each canonical key, so one page never gets two rows."""
    seen = {}
    for url in urls:
        seen.setdefault(match_key(url), url)
    return list(seen.values())


# 3. Dynamic Database Manager
class DatabaseManager:
    def __init__(self, database_name="blockurl.db", create_tables=False, initialize_settings=False):
        # Dynamically attach the chosen database name and custom optimization PRAGMAs
        db.init(database_name, pragmas={
            "journal_mode": "wal",
            "busy_timeout": 2000,
        })

        db.connect(reuse_if_open=True)

        if create_tables:
            # Columns must exist before create_tables indexes them, or SQLite indexes the name as a string literal.
            if URL.table_exists():
                self.migrate_add_columns()
            db.create_tables([URL, Setting])
        if initialize_settings:
            self.init_settings()

    def close(self):
        if not db.is_closed():
            db.close()

    # Migration ----------------------------------------------------------------------------------------------------
    def migrate_add_columns(self):
        """
        One-time migration for databases created before domain/match_key/created_at
        existed on the url table. Safe to call every startup: each piece
        checks current state first and is a no-op once applied.
        """
        table_name = URL._meta.table_name
        cursor = db.execute_sql(f"PRAGMA table_info({table_name})")
        existing_columns = [row[1] for row in cursor.fetchall()]

        migrator = SqliteMigrator(db)
        pending_migrations = []

        if "domain" not in existing_columns:
            pending_migrations.append(migrator.add_column(table_name, "domain", URL.domain))

        if "match_key" not in existing_columns:
            pending_migrations.append(migrator.add_column(table_name, "match_key", URL.match_key))

        if "created_at" not in existing_columns:
            # add_column with a peewee field that has a Python-side default
            # will NOT backfill existing rows (SQLite ALTER TABLE ADD COLUMN
            # just sets NULL for existing rows) - we backfill explicitly below.
            pending_migrations.append(migrator.add_column(table_name, "created_at", URL.created_at))

        if pending_migrations:
            migrate(*pending_migrations)

        # Backfill domain for any rows missing it (newly-added column, or
        # any rows that ended up with NULL/empty domain some other way).
        rows_needing_domain = list(URL.select().where(
            URL.domain.is_null() | (URL.domain == '')
        ))
        for row in rows_needing_domain:
            row.domain = self._extract_domain(row.url)
            row.save()

        self._repair_literal_indexes(table_name)

        # Backfill match_key for any rows stored before matching moved off the raw URL.
        rows_needing_key = list(URL.select().where(
            URL.match_key.is_null() | (URL.match_key == '')
        ))
        for row in rows_needing_key:
            row.match_key = match_key(row.url)
            row.save()

        # Backfill created_at for any rows missing it. This is the best
        # available approximation for pre-existing rows, not a true
        # historical value, since SQLite never recorded it before.
        # Stored as UTC to match the default on the field and how the
        # frontend interprets these timestamps.
        URL.update(created_at=datetime.datetime.now(timezone.utc)).where(
            URL.created_at.is_null()
        ).execute()

        self._ensure_indexes(migrator, table_name, existing_columns)

    def _repair_literal_indexes(self, table_name):
        """Rebuild any index an older version built on a column that did not exist yet."""
        for column in ("domain", "match_key", "created_at"):
            index_name = f"{table_name}_{column}"
            cursor = db.execute_sql(f"PRAGMA index_list({table_name})")
            if index_name not in {row[1] for row in cursor.fetchall()}:
                continue
            via_index = db.execute_sql(
                f'SELECT count(*) FROM "{table_name}" INDEXED BY "{index_name}" WHERE "{column}" IS NULL'
            ).fetchone()[0]
            via_table = db.execute_sql(
                f'SELECT count(*) FROM "{table_name}" NOT INDEXED WHERE "{column}" IS NULL'
            ).fetchone()[0]
            if via_index != via_table:
                db.execute_sql(f'DROP INDEX "{index_name}"')
                db.execute_sql(f'CREATE INDEX "{index_name}" ON "{table_name}" ("{column}")')

    def _ensure_indexes(self, migrator, table_name, columns_that_existed_before):
        """
        index=True on a peewee field only auto-creates the index when
        create_table() builds a brand-new table. Columns added afterward
        via migration need their indexes created explicitly.
        """
        cursor = db.execute_sql(f"PRAGMA index_list({table_name})")
        existing_indexes = {row[1] for row in cursor.fetchall()}

        pending = []
        if "domain" not in columns_that_existed_before:
            index_name = f"{table_name}_domain"
            if index_name not in existing_indexes:
                pending.append(migrator.add_index(table_name, ("domain",), False))

        if "match_key" not in columns_that_existed_before:
            index_name = f"{table_name}_match_key"
            if index_name not in existing_indexes:
                pending.append(migrator.add_index(table_name, ("match_key",), False))

        if "created_at" not in columns_that_existed_before:
            index_name = f"{table_name}_created_at"
            if index_name not in existing_indexes:
                pending.append(migrator.add_index(table_name, ("created_at",), False))

        if pending:
            migrate(*pending)

    # Settings Methods -------------------------------------------------------------------------------------------------
    def init_settings(self):
        self.create_setting("blocked_page_heading_text", "Blocked")
        self.create_setting("blocked_page_body_text", "This Page has been blocked by BlockURL")
        self.create_setting("blocked_page_button_text", "Unblock")

    def create_setting(self, key, value):
        Setting.insert(key=key, value=value).on_conflict_ignore().execute()
        return True

    def set_setting(self, key, value):
        Setting.insert(key=key, value=value).on_conflict_replace().execute()
        return True

    def delete_setting(self, key):
        Setting.delete().where(Setting.key == key).execute()
        return True

    def get_setting(self, key):
        setting = Setting.get_or_none(Setting.key == key)
        return setting.value if setting else None

    def get_all_settings(self):
        return [(s.key, s.value) for s in Setting.select()]

    # URL Methods ------------------------------------------------------------------------------------------------------
    @staticmethod
    def _extract_domain(url):
        netloc = urlparse(url).netloc
        if not netloc:
            netloc = urlparse(f"//{url}").netloc
        return netloc.lower()

    def set_urls(self, urls):
        """
        Block every URL in the list and report what happened, so an import
        can tell the user how much was new. "merged" covers everything that
        did not create a new row: URLs already blocked under any spelling of
        the same page, plus any repeated within this list. received == added
        + merged always holds.
        """
        if not urls:
            return {"received": 0, "added": 0, "merged": 0}
        unique_urls = list(dict.fromkeys(urls))
        blocked = self.get_urls_exist(unique_urls)
        new_urls = _first_per_key(url for url in unique_urls if not blocked[url])
        data = [
            {"url": url, "domain": self._extract_domain(url), "match_key": match_key(url)}
            for url in new_urls
        ]
        if data:
            URL.insert_many(data).on_conflict(
                conflict_target=[URL.url],
                update={URL.domain: EXCLUDED.domain, URL.match_key: EXCLUDED.match_key}
            ).execute()
        return {"received": len(urls), "added": len(data), "merged": len(urls) - len(data)}

    def delete_urls(self, urls):
        if not urls:
            return True
        URL.delete().where(URL.match_key << [match_key(url) for url in urls]).execute()
        return True

    def get_urls_exist(self, urls):
        """Report which URLs are blocked, matching on the canonical key rather than the raw URL."""
        if not urls:
            return {}
        keys = {url: match_key(url) for url in urls}
        matches = {u.match_key for u in URL.select(URL.match_key).where(URL.match_key << list(keys.values()))}
        return {url: keys[url] in matches for url in urls}

    def get_all_urls(self):
        return [u.url for u in URL.select(URL.url)]

    def get_urls_sorted(self, order_by="created_at", descending=True, domain=None):
        column_map = {
            "created_at": URL.created_at,
            "domain": URL.domain,
            "url": URL.url
        }
        if order_by not in column_map:
            raise ValueError(f"Invalid order_by column: {order_by}")

        query = URL.select(URL.url, URL.domain, URL.created_at)
        if domain:
            query = query.where(URL.domain == domain)

        order_attr = column_map[order_by].desc() if descending else column_map[order_by].asc()
        query = query.order_by(order_attr)
        return [(u.url, u.domain, str(u.created_at)) for u in query]

    def get_domains_with_counts(self):
        query = (URL
                 .select(URL.domain, fn.COUNT(URL.url).alias('count'))
                 .group_by(URL.domain)
                 .order_by(SQL('count DESC')))
        return [(row.domain, row.count) for row in query]

    def get_stats(self):
        """Headline numbers for the dashboard: how many URLs, across how many domains."""
        total_urls = URL.select().count()
        unique_domains = URL.select(fn.COUNT(fn.DISTINCT(URL.domain))).scalar() or 0
        return {"total_urls": total_urls, "unique_domains": unique_domains}