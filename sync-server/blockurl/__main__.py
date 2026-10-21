import logging
import os
from pathlib import Path


def read_secret_file(path):
    """The contents of a secret file with surrounding whitespace removed."""
    return Path(path).read_text().strip()


def launch_app():
    host = os.environ.get('BLOCKURL_HOST', '0.0.0.0')
    port = int(os.environ.get('BLOCKURL_PORT', 8000))
    database_path = os.environ.get('BLOCKURL_DATABASE_PATH', "blockurl.db")
    hashes_file = os.environ.get('BLOCKURL_API_KEY_HASHES_FILE', '').strip()
    storage_secret_file = os.environ.get('BLOCKURL_STORAGE_SECRET_FILE', '').strip()

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')

    # Sessions live next to the database, which is the one directory the server
    # is guaranteed to be allowed to write. NiceGUI reads this when it loads,
    # so it has to be set before anything imports it.
    os.environ.setdefault('NICEGUI_STORAGE_PATH', str(Path(database_path).resolve().parent / '.nicegui'))

    from nicegui import app, ui
    from .api import build_api
    from .auth import load_client_hashes, register_auth
    from .database import DatabaseManager
    from .pages import register_pages

    database = DatabaseManager(
        database_name=database_path,
        create_tables=True,
        initialize_settings=True
    )
    database.close()

    client_hashes = load_client_hashes(hashes_file) if hashes_file else {}
    storage_secret = read_secret_file(storage_secret_file) if storage_secret_file else None
    if client_hashes and not storage_secret:
        raise SystemExit('BLOCKURL_STORAGE_SECRET_FILE must name a non-empty file when client keys are configured')

    app.include_router(build_api(database))
    if client_hashes:
        register_auth(client_hashes)
    register_pages(database, auth_enabled=bool(client_hashes))

    ui.run(
        host=host,
        port=port,
        title='BlockURL Sync Server',
        favicon='🚫',
        dark=None,
        show=False,
        reload=False,
        storage_secret=storage_secret,
    )


if __name__ in {"__main__", "__mp_main__"}:
    launch_app()
