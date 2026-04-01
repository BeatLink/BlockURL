import os
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from .database import DatabaseManager
from .views import index_bp, init_settings, init_urls

def launch_app():
    host = os.environ.get('BLOCKURL_HOST', '0.0.0.0')
    port = int(os.environ.get('BLOCKURL_PORT', 8000))
    database_path = os.environ.get('DATABASE_PATH', "blockurl.db")
    database = DatabaseManager(
        database_name=database_path, 
        create_tables=True, 
        initialize_settings=True
    )
    app = Flask(__name__)
    app.register_blueprint(index_bp)
    app.register_blueprint(init_settings(database))
    app.register_blueprint(init_urls(database))
    asgi_app = WsgiToAsgi(app)
    uvicorn.run(asgi_app, host=host, port=port)

if __name__ == "__main__": 
    launch_app()