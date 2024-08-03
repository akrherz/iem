"""Test iemweb.request.metars module."""

from iemweb.request import metars
from werkzeug.test import Client


def test_load():
    """Test the requests."""
    c = Client(metars.application)
    metars.SIMULTANEOUS_REQUESTS = -1
    resp = c.get("/request/metars.py?valid=2020070100")
    metars.SIMULTANEOUS_REQUESTS = 10
    assert resp.status_code == 503
