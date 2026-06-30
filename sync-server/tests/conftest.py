import hashlib
import os
import tempfile

import pytest
from flask import Flask, request, jsonify, session, redirect

from blockurl.database import DatabaseManager, db
from blockurl.views import index_bp, init_login, init_settings, init_urls

TEST_API_KEY = "test-secret-key"


def _make_app(database, api_key=None):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flask_app = Flask(
        __name__,
        template_folder=os.path.join(here, "blockurl", "templates"),
        static_folder=os.path.join(here, "blockurl", "static"),
    )
    flask_app.config.update(TESTING=True)

    if api_key:
        flask_app.secret_key = hashlib.sha256(b'blockurl-session:' + api_key.encode()).digest()

    @flask_app.before_request
    def before_request():
        if api_key:
            path = request.path
            if path == '/login' or path.startswith('/static/'):
                pass
            elif request.headers.get('X-API-Key') == api_key:
                pass
            elif not session.get('authenticated'):
                return redirect(f'/login?next={path}')
        db.connect(reuse_if_open=True)

    @flask_app.teardown_request
    def teardown_request(exception=None):
        if not db.is_closed():
            db.close()

    flask_app.register_blueprint(index_bp)
    if api_key:
        flask_app.register_blueprint(init_login(api_key))
    flask_app.register_blueprint(init_settings(database))
    flask_app.register_blueprint(init_urls(database))
    return flask_app


@pytest.fixture
def database():
    """A fresh, file-backed SQLite database for each test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    db_manager = DatabaseManager(
        database_name=path,
        create_tables=True,
        initialize_settings=True,
    )
    yield db_manager

    db_manager.close()
    if not db.is_closed():
        db.close()
    os.unlink(path)


@pytest.fixture
def app(database):
    return _make_app(database)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_app(database):
    return _make_app(database, api_key=TEST_API_KEY)


@pytest.fixture
def auth_client(auth_app):
    return auth_app.test_client()
