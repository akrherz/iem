"""Exercise the mastodon configuration somewhat."""

import responses
from iemweb.projects.iembot.mastodon.index import (
    application,
)

# iem-database has a test entry for this.
TEST_HOST = "masto.globaleas.org"


def test_no_server_provided(wsgi_client):
    """Test request without a server set."""
    client = wsgi_client(application)
    resp = client.get("/projects/iembot/mastodon/")
    assert resp.status_code == 200
    assert b"Enter your Mastodon" in resp.data


def test_simple(wsgi_client):
    """Walk before we run here."""
    client = wsgi_client(application)
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            f"https://{TEST_HOST}/.well-known/oauth-authorization-server",
            status=200,
            json={
                "authorization_endpoint": (
                    f"https://{TEST_HOST}/oauth/authorize"
                ),
                "token_endpoint": f"https://{TEST_HOST}/oauth/token",
            },
        )
        resp = client.get(f"?s={TEST_HOST}")
        assert resp.status_code == 307


def test_oauth_code(wsgi_client):
    """Test the callback when oauth is done."""
    client = wsgi_client(application)
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            f"https://{TEST_HOST}/.well-known/oauth-authorization-server",
            status=200,
            json={
                "authorization_endpoint": (
                    f"https://{TEST_HOST}/oauth/authorize"
                ),
                "token_endpoint": f"https://{TEST_HOST}/oauth/token",
                "grant_types_supported": ["authorization_code"],
            },
        )
        rsps.add(
            responses.POST,
            f"https://{TEST_HOST}/oauth/token",
            status=200,
            json={
                "access_token": "fake_access_token",
                "token_type": "Bearer",
                "scope": "read write follow push",
            },
        )
        rsps.add(
            responses.GET,
            f"https://{TEST_HOST}/api/v2/instance/",
            status=200,
            json={
                "version": "4.4.3",
                "api_versions": {"mastodon": 6},
                "domain": TEST_HOST,
            },
        )
        rsps.add(
            responses.GET,
            f"https://{TEST_HOST}/api/v1/accounts/verify_credentials",
            status=200,
            json={
                "id": 12345,
                "username": "testuser",
                "acct": "testuser",
                "display_name": "Test User",
            },
        )
        resp = client.get(f"?code=fake_code&s={TEST_HOST}")
        assert resp.status_code == 200
