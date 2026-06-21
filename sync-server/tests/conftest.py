import os
import tempfile

import pytest
from flask import Flask

from blockurl.database import DatabaseManager, db
from blockurl.views import index_bp, init_settings, init_urls


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
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flask_app = Flask(
        __name__,
        template_folder=os.path.join(here, "blockurl", "templates"),
        static_folder=os.path.join(here, "blockurl", "static"),
    )

    @flask_app.before_request
    def before_request():
        db.connect(reuse_if_open=True)

    @flask_app.teardown_request
    def teardown_request(exception=None):
        if not db.is_closed():
            db.close()

    flask_app.register_blueprint(index_bp)
    flask_app.register_blueprint(init_settings(database))
    flask_app.register_blueprint(init_urls(database))
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()
