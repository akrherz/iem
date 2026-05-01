"""Exercise some things with afos/retrieve.py"""

from iemweb.afos import retrieve
from werkzeug.test import Client


def test_dsm_throttle():
    """Smoke test some code paths.."""
    client = Client(retrieve.application)
    eo = {"REMOTE_ADDR": "7.7.7.7"}
    response = client.get(
        "/cgi-bin/afos/retrieve.py?pil=DSM", environ_overrides=eo
    )
    assert response.status_code in [200, 429]


def test_query_timeout():
    """Test that we get a 503 when goosing the timeout."""
    original = retrieve.STATEMENT_TIMEOUT
    try:
        retrieve.STATEMENT_TIMEOUT = "1ms"
        client = Client(retrieve.application)
        eo = {"REMOTE_ADDR": "7.7.7.8"}
        response = client.get(
            "/cgi-bin/afos/retrieve.py?pil=AFD", environ_overrides=eo
        )
        assert response.status_code == 503
    finally:
        # Set it back for future tests to not be affected.
        retrieve.STATEMENT_TIMEOUT = original
