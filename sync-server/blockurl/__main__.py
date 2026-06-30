import os
import hashlib
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, request, jsonify, session, redirect
from .database import DatabaseManager, db
from .views import index_bp, init_login, init_settings, init_urls

def launch_app():
    host = os.environ.get('BLOCKURL_HOST', '0.0.0.0')
    port = int(os.environ.get('BLOCKURL_PORT', 8000))
    database_path = os.environ.get('BLOCKURL_DATABASE_PATH', "blockurl.db")
    api_key = os.environ.get('BLOCKURL_API_KEY', '').strip() or None
    database = DatabaseManager(
        database_name=database_path,
        create_tables=True,
        initialize_settings=True
    )
    database.close()

    app = Flask(__name__,
        template_folder='templates',
        static_folder='static'
    )

    if api_key:
        app.secret_key = hashlib.sha256(b'blockurl-session:' + api_key.encode()).digest()

    @app.before_request
    def before_request():
        if api_key:
            path = request.path
            if path == '/login' or path.startswith('/static/'):
                pass
            elif request.headers.get('X-API-Key') == api_key:
                pass
            elif not session.get('authenticated'):
                next_path = path
                return redirect(f'/login?next={next_path}')
        db.connect(reuse_if_open=True)

    @app.teardown_request
    def teardown_request(exception=None):
        if not db.is_closed():
            db.close()

    app.register_blueprint(index_bp)
    if api_key:
        app.register_blueprint(init_login(api_key))
    app.register_blueprint(init_settings(database))
    app.register_blueprint(init_urls(database))
    
    asgi_app = WsgiToAsgi(app)
    uvicorn.run(asgi_app, host=host, port=port)

if __name__ == "__main__": 
    launch_app()