"""Test iemweb.tilecache_dispatch."""

from iemweb import tilecache_dispatch
from werkzeug.test import Client


class _Body:
    """Iterable that tracks close()."""

    def __init__(self):
        self.closed = False

    def __iter__(self):
        return iter([b"tile"])

    def close(self):
        self.closed = True


def _stub(monkeypatch, route, headers=(), body=None):
    """Install a stub handler on a route."""

    def handler(_environ, start_response):
        start_response("200 OK", list(headers))
        return body if body is not None else [b"tile"]

    monkeypatch.setitem(tilecache_dispatch._ROUTES, route, handler)


def test_fallback_head_has_no_body():
    """HEAD on the fallback route yields no body bytes."""
    res = Client(tilecache_dispatch.application).head("/nope")
    assert res.status_code == 200
    assert res.get_data() == b""


def test_fallback_get_has_body():
    """GET on the fallback route still returns a body."""
    res = Client(tilecache_dispatch.application).get("/nope")
    assert res.get_data() == b"OK\n"


def test_routed_head_strips_body_and_closes(monkeypatch):
    """HEAD on a routed handler drops the body and closes the iterable."""
    body = _Body()
    _stub(monkeypatch, "/c/tile.py", [("Content-Length", "4")], body)
    res = Client(tilecache_dispatch.application).head("/c/tile.py/x")
    assert res.get_data() == b""
    assert body.closed
    assert res.headers["Content-Length"] == "4"
    assert "Cache-Control" in res.headers


def test_routed_get_passes_body(monkeypatch):
    """GET on a routed handler is passed through."""
    _stub(monkeypatch, "/c/tile.py")
    res = Client(tilecache_dispatch.application).get("/c/tile.py")
    assert res.get_data() == b"tile"


def test_cache_route_short_ttl(monkeypatch):
    """The /cache namespace gets a 5 minute TTL."""
    _stub(monkeypatch, "/cache/tile.py")
    res = Client(tilecache_dispatch.application).get("/cache/tile.py")
    assert res.headers["Cache-Control"] == "public, max-age=300"
    assert "Expires" in res.headers


def test_c_route_long_ttl(monkeypatch):
    """The /c namespace gets a 14 day TTL."""
    _stub(monkeypatch, "/c/tile.py")
    res = Client(tilecache_dispatch.application).get("/c/tile.py")
    assert res.headers["Cache-Control"] == (
        f"public, max-age={tilecache_dispatch.FOURTEEN_DAYS}"
    )


def test_existing_cache_headers_preserved(monkeypatch):
    """Handler-supplied cache headers are not overwritten."""
    _stub(
        monkeypatch,
        "/c/tile.py",
        [("Cache-Control", "no-store"), ("Expires", "never")],
    )
    res = Client(tilecache_dispatch.application).get("/c/tile.py")
    assert res.headers["Cache-Control"] == "no-store"
    assert res.headers["Expires"] == "never"
