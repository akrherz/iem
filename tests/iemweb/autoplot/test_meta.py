"""Test the metadata service."""

from iemweb.autoplot.meta import application, find_title, get_timing


def test_meta(wsgi_client):
    """Ensure that we test the front-end and not leave to PHP chance."""
    c = wsgi_client(application)
    resp = c.get("?p=0")  # This gets overview
    assert resp.status_code == 200
    resp = c.get("?p=1")
    assert resp.status_code == 200


def test_find_title():
    """Test what we get with an invalid pid."""
    assert "Unset?" in find_title(-1)


def test_simple():
    """Test the API."""
    res = get_timing(0)
    assert res == -1
