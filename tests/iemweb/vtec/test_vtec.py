"""Test things in vtec/{index,f}.py"""

from iemweb.vtec.f import application as f_app
from iemweb.vtec.index import application as index_app
from werkzeug.test import EnvironBuilder, run_wsgi_app


def test_index_unknown_vtec():
    """Test the index page."""
    builder = EnvironBuilder(
        path=(
            "/vtec/?year=2024&wfo=KDMX&phenomena=TO&"
            "significance=W&eventid=1045"
        ),
        base_url="https://iem.local/vtec/",
    )
    environ = builder.get_environ()
    (_app_iter, status, _headers) = run_wsgi_app(index_app, environ)
    assert status == "200 OK"


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
    environ["SCRIPT_URI"] = "/vtec/event/2024-O-NEW-KDMX-TO-W-0045/bah/bah"
    (_app_iter, status, headers) = run_wsgi_app(index_app, environ)
    assert status == "301 Moved Permanently"
    ans = "/vtec/?wfo=KDMX&phenomena=TO&significance=W&eventid=0045&year=2024"
    assert headers["Location"] == ans


def test_index_redirect():
    """Test the redirect."""
    builder = EnvironBuilder(
        path="/vtec/index.py",
        base_url="https://iem.local/vtec/",
        query_string="vtec=2024-O-NEW-KDMX-TO-W-0045",
    )
    environ = builder.get_environ()
    (_app_iter, status, _headers) = run_wsgi_app(index_app, environ)
    assert status == "301 Moved Permanently"
