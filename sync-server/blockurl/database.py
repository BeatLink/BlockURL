import datetime
from urllib.parse import urlparse
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.migrate import SqliteMigrator, migrate

# 1. Initialize an un-deferred database proxy
db = SqliteExtDatabase(None)  # Path is intentionally set to None initially


# 2. Declarative Models (Bound to the Proxy Database)
class BaseModel(Model):
    class Meta:
        database = db


class URL(BaseModel):
    url = CharField(primary_key=True)
    domain = CharField(null=True, index=True)
    created_at = DateTimeField(default=lambda: datetime.datetime.now(), index=True)


class Setting(BaseModel):
    key = CharField(primary_key=True)
    value = CharField()


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
            db.create_tables([URL, Setting])
            self.migrate_add_columns()
        if initialize_settings:
            self.init_settings()

    def close(self):
        if not db.is_closed():
            db.close()

    # Migration ----------------------------------------------------------------------------------------------------
    def migrate_add_columns(self):
        """
        One-time migration for databases created before domain/created_at
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

        # Backfill created_at for any rows missing it. This is the best
        # available approximation for pre-existing rows, not a true
        # historical value, since SQLite never recorded it before.
        URL.update(created_at=datetime.datetime.now()).where(
            URL.created_at.is_null()
        ).execute()

        self._ensure_indexes(migrator, table_name, existing_columns)

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
        if not urls:
            return True
        data = [{"url": url, "domain": self._extract_domain(url)} for url in urls]
        URL.insert_many(data).on_conflict(
            conflict_target=[URL.url],
            update={URL.domain: EXCLUDED.domain}
        ).execute()
        return True

    def delete_urls(self, urls):
        if not urls:
            return True
        URL.delete().where(URL.url << urls).execute()
        return True

    def get_urls_exist(self, urls):
        if not urls:
            return {}
        matches = {u.url for u in URL.select(URL.url).where(URL.url << urls)}
        return {url: url in matches for url in urls}

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