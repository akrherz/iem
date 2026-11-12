"""Test iemweb.request.metars module."""

from iemweb.request import metars


def test_load(wsgi_client):
    """Test the requests."""
    c = wsgi_client(metars.application)
    metars.SIMULTANEOUS_REQUESTS = -1
    resp = c.get("/request/metars.py?valid=2020070100")
    metars.SIMULTANEOUS_REQUESTS = 10
    assert resp.status_code == 503
