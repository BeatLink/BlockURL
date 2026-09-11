"""Optional API-key protection for the whole server.

The extension sends the key as an X-API-Key header; a person signs in once on
the login page and is remembered by a session cookie.
"""

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


def is_allowed(path, header_key, signed_in, api_key):
    """Whether a request may proceed instead of being sent to the login page."""
    return path.startswith(PUBLIC_PREFIXES) or header_key == api_key or bool(signed_in)


def safe_next_path(next_path):
    """Only ever redirect back to a path on this server."""
    if not next_path or not next_path.startswith('/') or '//' in next_path:
        return '/'
    return next_path


def register_auth(api_key):
    """Guard every route with the API key and add the login and logout routes."""

    async def guard(request: Request, call_next):
        path = request.url.path
        if path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)
        if is_allowed(path, request.headers.get('X-API-Key'), app.storage.user.get('authenticated'), api_key):
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
            if key_entry.value == api_key:
                app.storage.user['authenticated'] = True
                ui.navigate.to(destination)
            else:
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
