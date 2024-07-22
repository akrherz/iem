"""Test the handler, sort of."""

from iemweb.proxy_error_handler import application
from werkzeug.test import Client


def test_simple():
    """Test simple."""
    c = Client(application)
    res = c.get("/")
    assert res.status_code == 500
