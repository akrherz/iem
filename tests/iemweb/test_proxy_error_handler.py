"""Test the handler, sort of."""

from iemweb.proxy_error_handler import application


def test_simple(wsgi_client):
    """Test simple."""
    c = wsgi_client(application)
    res = c.get("/")
    assert res.status_code == 200
