"""The HTTP API the Firefox extension talks to.

Paths, payloads and status codes here are a contract with shipped copies of the
extension, so they stay exactly as they are.
"""

import html
from json import JSONDecodeError

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from .database import in_connection

MAX_URLS_PER_REQUEST = 10_000
MAX_URL_LENGTH = 2048


def _error(message):
    return JSONResponse({"error": message}, status_code=400)


async def _read_json(request):
    """Return the request body as JSON, or an error response if it is not JSON."""
    try:
        return await request.json(), None
    except (JSONDecodeError, UnicodeDecodeError, ValueError):
        return None, _error("expected a JSON body")


async def _run(call, *args, **kwargs):
    """Run a database call on a worker thread, off the event loop."""
    return await run_in_threadpool(in_connection, call, *args, **kwargs)


def _parse_urls(body):
    if not isinstance(body, dict) or "urls" not in body:
        return None, _error("missing 'urls'")
    raw = body["urls"]
    if not isinstance(raw, list) or len(raw) > MAX_URLS_PER_REQUEST:
        return None, _error(f"'urls' must be a list of at most {MAX_URLS_PER_REQUEST} items")
    if any(not isinstance(u, str) or len(u) > MAX_URL_LENGTH for u in raw):
        return None, _error(f"each URL must be a string of at most {MAX_URL_LENGTH} characters")
    return [html.unescape(u) for u in raw], None


async def _urls_from(request):
    """Read and validate the URL list a request carries."""
    body, error = await _read_json(request)
    if error:
        return None, error
    return _parse_urls(body)


def build_api(database):
    """Build the router carrying every API route."""
    router = APIRouter()

    # Settings ---------------------------------------------------------------------------------------------------------
    @router.get('/settings/all')
    async def settings_all():
        return await _run(database.get_all_settings)

    @router.post('/settings/get')
    async def settings_get(request: Request):
        body, error = await _read_json(request)
        if error:
            return error
        if not isinstance(body, dict) or "key" not in body:
            return _error("missing 'key'")
        return await _run(database.get_setting, body["key"])

    @router.post('/settings/set')
    async def settings_set(request: Request):
        body, error = await _read_json(request)
        if error:
            return error
        if not isinstance(body, dict) or "key" not in body or "value" not in body:
            return _error("missing 'key' or 'value'")
        return await _run(database.set_setting, body["key"], body["value"])

    # URLs -------------------------------------------------------------------------------------------------------------
    @router.get('/urls/all')
    async def urls_all():
        return await _run(database.get_all_urls)

    @router.post('/urls/check')
    async def urls_check(request: Request):
        urls, error = await _urls_from(request)
        if error:
            return error
        return await _run(database.get_urls_exist, urls)

    @router.post('/urls/block')
    async def urls_block(request: Request):
        urls, error = await _urls_from(request)
        if error:
            return error
        return await _run(database.set_urls, urls)

    @router.post('/urls/unblock')
    async def urls_unblock(request: Request):
        urls, error = await _urls_from(request)
        if error:
            return error
        return await _run(database.delete_urls, urls)

    @router.post('/urls/sorted')
    async def urls_sorted(request: Request):
        body, error = await _read_json(request)
        if error:
            return error
        body = body if isinstance(body, dict) else {}
        domain = body.get("domain")
        try:
            results = await _run(
                database.get_urls_sorted,
                order_by=body.get("order_by", "created_at"),
                descending=body.get("descending", True),
                domain=html.unescape(domain) if domain is not None else None,
            )
        except ValueError as e:
            return _error(str(e))
        return [
            {"url": url, "domain": domain, "created_at": created_at}
            for url, domain, created_at in results
        ]

    @router.get('/urls/domains')
    async def urls_domains():
        return await _run(database.get_domains_with_counts)

    @router.get('/urls/stats')
    async def urls_stats():
        return await _run(database.get_stats)

    return router
