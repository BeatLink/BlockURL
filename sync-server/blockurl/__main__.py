import hashlib
import os
from pathlib import Path


def launch_app():
    host = os.environ.get('BLOCKURL_HOST', '0.0.0.0')
    port = int(os.environ.get('BLOCKURL_PORT', 8000))
    database_path = os.environ.get('BLOCKURL_DATABASE_PATH', "blockurl.db")
    api_key = os.environ.get('BLOCKURL_API_KEY', '').strip() or None

    # Sessions live next to the database, which is the one directory the server
    # is guaranteed to be allowed to write. NiceGUI reads this when it loads,
    # so it has to be set before anything imports it.
    os.environ.setdefault('NICEGUI_STORAGE_PATH', str(Path(database_path).resolve().parent / '.nicegui'))

    from nicegui import app, ui
    from .api import build_api
    from .auth import register_auth
    from .database import DatabaseManager
    from .pages import register_pages

    database = DatabaseManager(
        database_name=database_path,
        create_tables=True,
        initialize_settings=True
    )
    database.close()

    app.include_router(build_api(database))
    if api_key:
        register_auth(api_key)
    register_pages(database, api_key)

    ui.run(
        host=host,
        port=port,
        title='BlockURL Sync Server',
        favicon='🚫',
        dark=None,
        show=False,
        reload=False,
        storage_secret=hashlib.sha256(b'blockurl-session:' + api_key.encode()).hexdigest() if api_key else None,
    )


if __name__ in {"__main__", "__mp_main__"}:
    launch_app()
