"""Test iemweb.request.asos module."""

from iemweb.request.asos import application
from werkzeug.test import Client


def test_asos_request():
    """Test too much data with the request."""
    client = Client(application, None)
    resp = client.get(
        "?sts=1900-01-01T00:00Z"
        "&station=AWM,DSM,ALO,OTM,BRL,DBQ,CID,IOW,MCW,MIW"
        "&ets=2026-01-01T00:00Z&format=comma"
    )
    # exhaust the generator for coverage purposes
    list(resp.response)
    assert resp.status_code == 400


def test_asos_alldata_greater_than_24hours():
    """Test that we don't allow this request either."""
    client = Client(application, None)
    resp = client.get(
        "?sts=1900-01-01T00:00Z&ets=2026-01-01T00:00Z&format=comma"
    )
    # exhaust the generator for coverage purposes
    list(resp.response)
    assert resp.status_code == 400
