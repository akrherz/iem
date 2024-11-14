"""Test things in vtec/{index,f}.py"""

from iemweb.vtec.f import application as f_app
from iemweb.vtec.index import application as index_app
from werkzeug.test import Client, EnvironBuilder, run_wsgi_app


def test_f_http_redirect():
    """Test the redirect for non https requests."""
    builder = EnvironBuilder(
        path="/vtec/f/2024-O-NEW-KDMX-TO-W-0045",
        base_url="https://iem.local/vtec/",
    )
    environ = builder.get_environ()
    environ["SCRIPT_URI"] = "/vtec/f/2024-O-NEW-KDMX-TO-W-0045"
    (_app_iter, status, _headers) = run_wsgi_app(f_app, environ)
    assert status == "200 OK"


def test_index_http_redirect():
    """Test the redirect for non https requests."""
    builder = EnvironBuilder(
        path="/vtec/event/2024-O-NEW-KDMX-TO-W-0045",
        base_url="https://iem.local/vtec/",
    )
    environ = builder.get_environ()
    environ["SCRIPT_URI"] = "/vtec/event/2024-O-NEW-KDMX-TO-W-0045"
    (_app_iter, status, _headers) = run_wsgi_app(index_app, environ)
    assert status == "200 OK"


def test_index_redirect():
    """Test the redirect."""
    c = Client(index_app)
    resp = c.get("?vtec=2024-O-NEW-KDMX-TO-W-0045")
    assert resp.status_code == 301
