"""Tests for the shared /json, /geojson, and /search dispatcher."""

from iemweb.dispatch import application
from werkzeug.test import Client


def test_shared_json_mount():
    """Ensure the shared handler dispatches /json via SCRIPT_NAME."""
    client = Client(application, response_wrapper=None)
    response = client.get(
        "/stage4/-97.5/40.0/2026-03-01",
        environ_overrides={"SCRIPT_NAME": "/json"},
    )
    assert response.status_code == 200
    assert "gridi" in response.json


def test_shared_geojson_mount():
    """Ensure the shared handler dispatches /geojson via SCRIPT_NAME."""
    client = Client(application, response_wrapper=None)
    response = client.get(
        "/network_obs.php",
        environ_overrides={"SCRIPT_NAME": "/geojson"},
    )
    assert response.status_code == 302


def test_direct_search_route():
    """Ensure /search dispatches directly to iemweb.search via PATH_INFO."""
    client = Client(application, response_wrapper=None)
    response = client.get("/search?q=DSM")
    assert response.status_code == 302
