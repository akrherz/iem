"""Test geojson/sbw.py service."""

import json

from iemweb.geojson.sbw import application
from werkzeug.test import Client


def test_250102_ts_not_working():
    """Test a failure found in prod."""
    c = Client(application)
    res = c.get("?ts=2024-05-21T20:00:00Z")
    assert res is not None
    jdata = json.loads(res.data.decode("utf-8"))
    assert jdata is not None
    assert jdata["features"]
