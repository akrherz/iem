"""Test specialized things we are attempting to handle."""

from functools import partial

import pytest
from iemweb.dispatch import dispatch_namespace
from werkzeug.test import Client


@pytest.fixture
def myapp():
    """Return our application."""
    return partial(dispatch_namespace, "geojson")


def test_invalid(myapp):
    """Test that invalid request goes to our /api/ page."""
    c = Client(myapp, response_wrapper=None)
    resp = c.get("/yo_yo_yo")
    assert resp.status_code == 301


def test_7am(myapp):
    """Test a poor live choice."""
    c = Client(myapp, response_wrapper=None)
    resp = c.get("/7am.geojson")
    assert resp.status_code == 200


def test_network_obs(myapp):
    """Test that this gets redirected."""
    c = Client(myapp, response_wrapper=None)
    resp = c.get("/network_obs.php")
    assert resp.status_code == 302


def test_nexrad_attr_csv(myapp):
    """Test another one off."""
    c = Client(myapp, response_wrapper=None)
    resp = c.get("/nexrad_attr.csv")
    assert resp.status_code == 200
    assert "," in resp.text


def test_network(myapp):
    """Try this."""
    c = Client(myapp, response_wrapper=None)
    resp = c.get("/network/IA_ASOS.geojson")
    assert "features" in resp.get_json()
