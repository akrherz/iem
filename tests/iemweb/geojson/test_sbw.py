"""Test geojson/sbw.py service."""

from iemweb.geojson.sbw import application
from werkzeug.test import Client


def test_250102_ts_not_working():
    """Test a failure found in prod."""
    c = Client(application)
    res = c.get("?ts=2024-05-21T20:00:00Z")
    assert res.json["features"]
