import os
import tempfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from blockurl.api import build_api
from blockurl.database import DatabaseManager, db

TEST_API_KEY = "test-secret-key"


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
    """The API on a bare FastAPI app, without the NiceGUI frontend around it."""
    api_app = FastAPI()
    api_app.include_router(build_api(database))
    return api_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(autouse=True)
def ui_environment(request, monkeypatch, tmp_path):
    """Configure the entry point the UI tests run, before NiceGUI builds the app."""
    monkeypatch.setenv("BLOCKURL_DATABASE_PATH", str(tmp_path / "blockurl.db"))
    marker = request.node.get_closest_marker("blockurl_api_key")
    if marker:
        monkeypatch.setenv("BLOCKURL_API_KEY", marker.args[0])
    else:
        monkeypatch.delenv("BLOCKURL_API_KEY", raising=False)
