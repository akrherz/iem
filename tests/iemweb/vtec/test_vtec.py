"""Test things in vtec/{index,f}.py"""

from iemweb.vtec.f import application as f_app
from iemweb.vtec.index import application as index_app
from werkzeug.test import EnvironBuilder, run_wsgi_app


def test_index_unknown_vtec():
    """Test the index page."""
    builder = EnvironBuilder(
        path="/vtec/event/2024-O-NEW-KDMX-TO-W-1045",
        base_url="https://iem.local/vtec/",
    )
    environ = builder.get_environ()
    environ["SCRIPT_URI"] = "/vtec/event/2024-O-NEW-KDMX-TO-W-1045"
    (app_iter, status, _headers) = run_wsgi_app(index_app, environ)
    response_text = "".join([x.decode("utf-8") for x in app_iter])
    assert "2024-O-NEW-KDMX-TO-W-1045" in response_text
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
        base_url="http://iem.local/vtec/",
    )
    environ = builder.get_environ()
    environ["SCRIPT_URI"] = "/vtec/event/2024-O-NEW-KDMX-TO-W-0045"
    (_app_iter, status, _headers) = run_wsgi_app(index_app, environ)
    assert status == "301 Moved Permanently"


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
