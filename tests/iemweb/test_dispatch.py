"""Tests for the shared /json and /geojson dispatcher."""

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
