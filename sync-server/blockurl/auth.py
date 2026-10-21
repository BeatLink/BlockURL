"""Optional API-key protection for the whole server.

Each client has its own key, and the server keeps only a SHA-256 digest of it.
The extension sends its key as an X-API-Key header; a person signs in once on
the login page and is remembered by a session cookie.
"""

import hashlib
import hmac
import json
import logging

import nicegui
from fastapi import Request
from fastapi.responses import RedirectResponse
from nicegui import app, ui
from starlette.middleware.base import BaseHTTPMiddleware

from . import theme

# The login page, the websocket, and NiceGUI's own assets have to load before
# anyone can be signed in. Everything else under /_nicegui, including the
# per-page upload endpoints, stays behind the guard.
PUBLIC_PREFIXES = ('/login', '/_nicegui_ws', f'/_nicegui/{nicegui.__version__}/')

# API requests that change stored data, logged with the client that made them.
WRITE_PATHS = ('/settings/set', '/urls/block', '/urls/unblock')

logger = logging.getLogger('blockurl.auth')


def hash_key(key):
    """The hex SHA-256 digest a client's key is stored as."""
    return hashlib.sha256(key.encode()).hexdigest()


def load_client_hashes(path):
    """Read a JSON object mapping each client name to its key's hex SHA-256 digest."""
    with open(path) as file:
        client_hashes = json.load(file)
    if not isinstance(client_hashes, dict):
        raise ValueError(f'{path} must hold a JSON object of client name to key hash')
    for name, digest in client_hashes.items():
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdefABCDEF' for c in digest):
            raise ValueError(f'{path}: the hash for client {name!r} is not a hex SHA-256 digest')
    return {name: digest.lower() for name, digest in client_hashes.items()}


def match_client(key, client_hashes):
    """The name of the client whose key this is, or None."""
    if not key:
        return None
    digest = hash_key(key)
    matched = None
    # Every entry is compared so the time taken does not reveal which one matched.
    for name, stored in client_hashes.items():
        if hmac.compare_digest(digest, stored) and matched is None:
            matched = name
    return matched


def is_allowed(path, client_name, signed_in):
    """Whether a request may proceed instead of being sent to the login page."""
    return path.startswith(PUBLIC_PREFIXES) or client_name is not None or bool(signed_in)


def safe_next_path(next_path):
    """Only ever redirect back to a path on this server."""
    if not next_path or not next_path.startswith('/') or '//' in next_path:
        return '/'
    return next_path


def register_auth(client_hashes):
    """Guard every route with the client keys and add the login and logout routes."""

    async def guard(request: Request, call_next):
        path = request.url.path
        if path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)
        client_name = match_client(request.headers.get('X-API-Key'), client_hashes)
        if is_allowed(path, client_name, app.storage.user.get('authenticated')):
            if client_name is not None and path in WRITE_PATHS:
                logger.info('client %s called %s', client_name, path)
            return await call_next(request)
        return RedirectResponse(f'/login?next={path}', status_code=302)

    app.add_middleware(BaseHTTPMiddleware, dispatch=guard)

    @app.get('/logout')
    def logout():
        app.storage.user.clear()
        return RedirectResponse('/login', status_code=302)

    @ui.page('/login')
    def login_page(next: str = '/'):
        theme.apply_theme()
        ui.dark_mode(None)
        destination = safe_next_path(next)

        def submit():
            client_name = match_client(key_entry.value, client_hashes)
            if client_name is not None:
                logger.info('client %s signed in to the web UI', client_name)
                app.storage.user['authenticated'] = True
                app.storage.user['client'] = client_name
                ui.navigate.to(destination)
            else:
                logger.warning('failed web UI sign-in')
                error.set_visibility(True)

        with ui.column().classes('halon-login'):
            with ui.card().classes('halon-card halon-login-card'):
                ui.label('BlockURL').classes('halon-brand')
                error = ui.row().classes('halon-alert halon-alert-danger')
                with error:
                    ui.icon('error_outline')
                    ui.label('Invalid API key - please try again.')
                error.set_visibility(False)
                with ui.column().classes('halon-field w-full'):
                    ui.label('API Key').classes('halon-label')
                    key_entry = ui.input(placeholder='Paste your API key') \
                        .props('outlined dense type=password autofocus autocomplete=current-password') \
                        .classes('halon-input w-full').mark('api-key').on('keydown.enter', submit)
                ui.button('Sign in', color=None, on_click=submit).classes('halon-btn halon-btn-filled w-full')
