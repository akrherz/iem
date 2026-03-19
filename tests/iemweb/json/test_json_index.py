"""Test specialized things we are attempting to handle."""

from functools import partial

from iemweb.dispatch import dispatch_namespace
from werkzeug.test import Client

application = partial(dispatch_namespace, "json")


def test_invalid():
    """Test that invalid request goes to our /api/ page."""
    c = Client(application, response_wrapper=None)
    resp = c.get("/yo_yo_yo")
    assert resp.status_code == 301


def test_raob():
    """Test The raob rewrite."""
    c = Client(application, response_wrapper=None)
    resp = c.get("/raob/202603100000/KALB")
    assert resp.status_code == 200


def test_stage4():
    """Test the stage4 rewrite."""
    c = Client(application, response_wrapper=None)
    resp = c.get("/stage4/-97.5/40.0/2026-03-01")
    assert "gridi" in resp.json
    assert resp.status_code == 200


def test_index_php():
    """Test that index.php does not go into recursion."""
    c = Client(application, response_wrapper=None)
    resp = c.get("/index.php")
    assert resp.status_code == 301
