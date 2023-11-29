import sqlite3


class DatabaseManager:
    # Common Methods ---------------------------------------------------------------------------------------------------
    def __init__(self, database_name="blockurl.db", create_tables=False, initialize_settings=False):
        self.database_name = database_name
        if create_tables:
            self.create_all_tables()
        if initialize_settings:
            self.init_settings()

    def _get_database_(self):
        return sqlite3.connect(self.database_name)

    def create_all_tables(self):
        database = self._get_database_()
        cursor = database.cursor()
        create_table_statements = [
            """CREATE TABLE IF NOT EXISTS urls (url TEXT PRIMARY KEY)""",
            """CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"""
        ]
        for statement in create_table_statements:
            cursor.execute(statement)

    # Settings Methods -------------------------------------------------------------------------------------------------
    def init_settings(self):
        self.create_setting("blocked_page_heading_text", "Blocked")
        self.create_setting("blocked_page_body_text", "This Page has been blocked by BlockURL")
        self.create_setting("blocked_page_button_text", "Unblock")

    def create_setting(self, key, value):
        database = self._get_database_()
        cursor = database.cursor()
        statement = "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)"
        cursor.execute(statement, [key, value])
        database.commit()
        return True

    def set_setting(self, key, value):
        database = self._get_database_()
        cursor = database.cursor()
        statement = "UPDATE settings SET key = ?, value = ? WHERE key = ?"
        cursor.execute(statement, [key, value, key])
        database.commit()
        return True

    def delete_setting(self, key):
        database = self._get_database_()
        cursor = database.cursor()
        statement = "DELETE FROM settings WHERE key = ?"
        cursor.execute(statement, [key])
        database.commit()
        return True

    def get_setting(self, key):
        database = self._get_database_()
        cursor = database.cursor()
        statement = "SELECT value FROM settings WHERE key = ?"
        cursor.execute(statement, [key])
        data = cursor.fetchone()
        if data:
            return data[0]

    def get_all_settings(self):
        database = self._get_database_()
        cursor = database.cursor()
        query = "SELECT key, value FROM settings"
        cursor.execute(query)
        return cursor.fetchall()

    # URL Methods ------------------------------------------------------------------------------------------------------
    def set_url(self, url):
        database = self._get_database_()
        cursor = database.cursor()
        statement = "INSERT OR REPLACE INTO urls(url) VALUES (?)"
        cursor.execute(statement, [url])
        database.commit()
        return True

    def delete_url(self, url):
        database = self._get_database_()
        cursor = database.cursor()
        statement = "DELETE FROM urls WHERE url = ?"
        print(cursor.execute(statement, [url]))
        database.commit()
        return True

    def get_url_exists(self, url):
        database = self._get_database_()
        cursor = database.cursor()
        statement = "SELECT url FROM urls WHERE url = ?"
        cursor.execute(statement, [url])
        data = cursor.fetchall()
        return len(data) > 0

    def get_all_urls(self):
        database = self._get_database_()
        cursor = database.cursor()
        query = "SELECT url FROM urls"
        cursor.execute(query)
        return [url[0] for url in cursor.fetchall()]
