import json
import os
import tempfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from blockurl.api import build_api
from blockurl.auth import hash_key
from blockurl.database import DatabaseManager, db

TEST_CLIENT_KEYS = {"laptop": "laptop-secret-key", "phone": "phone-secret-key"}


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
    marker = request.node.get_closest_marker("blockurl_client_keys")
    if marker:
        hashes_file = tmp_path / "api-key-hashes.json"
        hashes_file.write_text(json.dumps({name: hash_key(key) for name, key in marker.args[0].items()}))
        secret_file = tmp_path / "storage-secret"
        secret_file.write_text("test-storage-secret\n")
        monkeypatch.setenv("BLOCKURL_API_KEY_HASHES_FILE", str(hashes_file))
        monkeypatch.setenv("BLOCKURL_STORAGE_SECRET_FILE", str(secret_file))
    else:
        monkeypatch.delenv("BLOCKURL_API_KEY_HASHES_FILE", raising=False)
        monkeypatch.delenv("BLOCKURL_STORAGE_SECRET_FILE", raising=False)
