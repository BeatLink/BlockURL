import os
from flask import Flask
from .database import DatabaseManager
from .views import index_bp, init_settings, init_urls

database = DatabaseManager(
    database_name=os.environ['DATABASE_PATH'], 
    create_tables=True, 
    initialize_settings=True
)
app = Flask(__name__)
app.register_blueprint(index_bp)
app.register_blueprint(init_settings(database))
app.register_blueprint(init_urls(database))

def main():
    host = os.environ.get('BLOCKURL_HOST', '0.0.0.0')
    port = int(os.environ.get('BLOCKURL_PORT', 8000))
    app.run(host=host, port=port, debug=True)
