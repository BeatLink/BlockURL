import os
from flask import Flask
from .database import DatabaseManager
from .views import index_bp, init_settings, init_urls

def create_app(database):
    app = Flask(__name__)
    app.register_blueprint(index_bp)
    app.register_blueprint(init_settings(database))
    app.register_blueprint(init_urls(database))
    return app

def launch_app():
    database = DatabaseManager(
        database_name=os.environ['DATABASE_PATH'], 
        create_tables=True, 
        initialize_settings=True
    )
    app = create_app(database)
    app.run(host='0.0.0.0', port=8000, debug=True)

if __name__ == '__main__':
    launch_app()