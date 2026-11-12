"""Test things in vtec/{index,f}.py"""

from iemweb.vtec.f import application as f_app
from iemweb.vtec.index import application as index_app


def test_index_unknown_vtec(wsgi_client):
    """Test the index page."""
    c = wsgi_client(index_app)
    resp = c.get(
        "/vtec/?year=2024&wfo=KDMX&phenomena=TO&significance=W&eventid=1045",
        environ_overrides={"wsgi.url_scheme": "https"},
    )
    assert resp.status_code == 200
    assert "Yikes!" in resp.text


def test_f_http_redirect(wsgi_client):
    """Test the redirect for non https requests."""
    client = wsgi_client(f_app)
    response = client.get(
        "/vtec/f/2024-O-NEW-KDMX-TO-W-0045",
        base_url="https://iem.local/vtec/",
        environ_overrides={"SCRIPT_URI": "/vtec/f/2024-O-NEW-KDMX-TO-W-0045"},
    )
    assert response.status_code == 200


def test_index_http_redirect(wsgi_client):
    """Test the redirect for non https requests."""
    client = wsgi_client(index_app)
    response = client.get(
        "/vtec/event/2024-O-NEW-KDMX-TO-W-0045",
        base_url="https://iem.local/vtec/",
        environ_overrides={
            "SCRIPT_URI": "/vtec/event/2024-O-NEW-KDMX-TO-W-0045/bah/bah"
        },
    )
    assert response.status_code == 301
    ans = "/vtec/?wfo=KDMX&phenomena=TO&significance=W&eventid=0045&year=2024"
    assert response.headers["Location"] == ans


def test_index_redirect(wsgi_client):
    """Test the redirect."""
    client = wsgi_client(index_app)
    response = client.get(
        "/vtec/index.py?vtec=2024-O-NEW-KDMX-TO-W-0045",
        base_url="https://iem.local/vtec/",
    )
    assert response.status_code == 301
