"""Exercise some things with afos/retrieve.py"""

from iemweb.afos import retrieve
from werkzeug.test import Client


def test_query_timeout():
    """Test that we get a 503 when goosing the timeout."""
    retrieve.STATEMENT_TIMEOUT = "1ms"
    client = Client(retrieve.application)
    response = client.get("/cgi-bin/afos/retrieve.py?pil=AFD")
    assert response.status_code == 503
