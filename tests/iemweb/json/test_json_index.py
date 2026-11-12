"""Test specialized things we are attempting to handle."""

from functools import partial

from iemweb.dispatch import dispatch_namespace

application = partial(dispatch_namespace, "json")


def test_invalid(wsgi_client):
    """Test that invalid request goes to our /api/ page."""
    c = wsgi_client(application)
    resp = c.get("/yo_yo_yo")
    assert resp.status_code == 301


def test_raob(wsgi_client):
    """Test The raob rewrite."""
    c = wsgi_client(application)
    resp = c.get("/raob/202603100000/KALB")
    assert resp.status_code == 200


def test_stage4(wsgi_client):
    """Test the stage4 rewrite."""
    c = wsgi_client(application)
    resp = c.get("/stage4/-97.5/40.0/2026-03-01")
    assert "gridi" in resp.get_json()
    assert resp.status_code == 200


def test_index_php(wsgi_client):
    """Test that index.php does not go into recursion."""
    c = wsgi_client(application)
    resp = c.get("/index.php")
    assert resp.status_code == 301
