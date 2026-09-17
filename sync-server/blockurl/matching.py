"""Reduces a URL to the canonical key that decides whether two URLs mean the same page.

Blocking records the URL exactly as the browser saw it, but a page is reachable
under several spellings at once: an embedded player, a share link and the page
itself all point at the same thing. Matching happens on the key, not the URL.
"""

from urllib.parse import parse_qsl, urlencode, urlsplit

DEFAULT_PORTS = {"http": "80", "https": "443"}

TRACKING_PARAMETERS = {"fbclid", "gclid", "igshid", "msclkid", "mc_eid"}

MEDIA_SUFFIXES = ("-mobile", "-small", "-large", "-silent", "-poster")

MEDIA_EXTENSIONS = (".mp4", ".webm", ".m4s", ".jpg", ".jpeg", ".png", ".webp", ".gif")


def match_key(url):
    """Return the canonical key for a URL, or the trimmed URL when it is not a web address."""
    url = (url or "").strip()
    split = urlsplit(url)
    if split.scheme and split.scheme not in DEFAULT_PORTS:
        return url
    if not split.netloc:
        split = urlsplit(f"//{url}")
    host = _host(split)
    if not host:
        return url
    host, path = _rewrite(host, split.path)
    return f"{host}{path}{_query(split.query)}"


def _host(split):
    """Return the lowercased hostname with any port and leading www. removed."""
    try:
        host = (split.hostname or "").lower()
    except ValueError:
        return ""
    port = _port(split)
    host = host[4:] if host.startswith("www.") else host
    return f"{host}:{port}" if port else host


def _port(split):
    """Return the port when it is not the default one for the scheme."""
    try:
        port = split.port
    except ValueError:
        return ""
    if not port or str(port) == DEFAULT_PORTS.get(split.scheme or "https"):
        return ""
    return str(port)


def _query(query):
    """Return the query string with tracking parameters dropped and the rest in a fixed order."""
    pairs = [
        (key, value) for key, value in parse_qsl(query, keep_blank_values=True)
        if key.lower() not in TRACKING_PARAMETERS and not key.lower().startswith("utm_")
    ]
    return f"?{urlencode(sorted(pairs))}" if pairs else ""


def _rewrite(host, path):
    """Apply the per-site rules that fold a site's alternate spellings onto one page."""
    path = "/" + path.strip("/")
    if host == "redgifs.com" or host.endswith(".redgifs.com"):
        return _redgifs(host, path)
    return host, "" if path == "/" else path


def _redgifs(host, path):
    """Fold redgifs embed, share and media URLs onto the watch page they belong to."""
    segments = [segment for segment in path.split("/") if segment]
    if host in ("redgifs.com", "v3.redgifs.com") and len(segments) == 2 and segments[0] in ("watch", "ifr", "i"):
        return "redgifs.com", f"/watch/{segments[1].lower()}"
    if segments and (host.startswith("media") or host.startswith("thumbs")):
        return "redgifs.com", f"/watch/{_media_identifier(segments[-1])}"
    return host, "" if path == "/" else path


def _media_identifier(filename):
    """Return the watch identifier a redgifs media filename is built from."""
    name = filename.lower()
    for extension in MEDIA_EXTENSIONS:
        if name.endswith(extension):
            name = name[: -len(extension)]
            break
    for suffix in MEDIA_SUFFIXES:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name
