"""Test geojson/sbw.py service."""

import json

from iemweb.geojson.sbw import application
from werkzeug.test import Client


def test_260410_ts_at_issue():
    """Test that we get a warning issued at the given timestamp."""
    c = Client(application)
    resp = c.get("?ts=2018-06-20T20:02:00Z")
    jdata = resp.get_json()
    found = False
    for feat in jdata["features"]:
        if feat["properties"]["eventid"] == 21:
            found = True
    assert found


def test_250102_ts_not_working():
    """Test a failure found in prod."""
    c = Client(application)
    res = c.get("?ts=2024-05-21T20:00:00Z")
    assert res is not None
    jdata = json.loads(res.data.decode("utf-8"))
    assert jdata is not None
    assert jdata["features"]
