"""Test iemweb.request.asos module."""

from iemweb.request.asos import application


def test_asos_request(wsgi_client):
    """Test too much data with the request."""
    client = wsgi_client(application)
    resp = client.get(
        "?sts=1900-01-01T00:00Z"
        "&station=AWM,DSM,ALO,OTM,BRL,DBQ,CID,IOW,MCW,MIW"
        "&ets=2026-01-01T00:00Z&format=comma"
    )
    # exhaust the generator for coverage purposes
    payload = "".join(resp.text)
    assert resp.status_code == 400, payload


def test_asos_alldata_greater_than_24hours(wsgi_client):
    """Test that we don't allow this request either."""
    client = wsgi_client(application)
    resp = client.get(
        "?sts=1900-01-01T00:00Z&ets=2026-01-01T00:00Z&format=comma"
    )
    # exhaust the generator for coverage purposes
    payload = "".join(resp.text)
    assert resp.status_code == 400, payload
