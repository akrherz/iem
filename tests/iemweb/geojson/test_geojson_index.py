"""Test specialized things we are attempting to handle."""

from iemweb.geojson.index import application
from werkzeug.test import Client


def test_invalid():
    """Test that invalid request goes to our /api/ page."""
    c = Client(application, response_wrapper=None)
    resp = c.get("yo_yo_yo")
    assert resp.status_code == 302


def test_7am():
    """Test a poor live choice."""
    c = Client(application, response_wrapper=None)
    resp = c.get("7am.geojson")
    assert resp.status_code == 200


def test_network_obs():
    """Test that this gets redirected."""
    c = Client(application, response_wrapper=None)
    resp = c.get("/network_obs.php")
    assert resp.status_code == 302


def test_nexrad_attr_csv():
    """Test another one off."""
    c = Client(application, response_wrapper=None)
    resp = c.get("/nexrad_attr.csv")
    assert resp.status_code == 200
    assert "," in resp.text


def test_network():
    """Try this."""
    c = Client(application, response_wrapper=None)
    resp = c.get("/network/IA_ASOS.geojson")
    assert "features" in resp.json
