from flask import Flask
from .database import DatabaseManager
from .views import IndexView, SettingsView, UrlsView

app = Flask(__name__)
database = DatabaseManager(database_name="/app/database/blockurl.db", create_tables=True, initialize_settings=True)
IndexView.register(app)
SettingsView.register(app, init_argument=database)
UrlsView.register(app, init_argument=database)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

