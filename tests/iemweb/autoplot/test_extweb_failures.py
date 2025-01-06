"""Test autoplots that call external services."""

from iemweb.autoplot.autoplot import application
from pytest_httpx import HTTPXMock
from werkzeug.test import Client


def test_ap17(httpx_mock: HTTPXMock):
    """Test a failure found in prod."""
    httpx_mock.add_response(status_code=404)
    c = Client(application)
    res = c.get("?p=17&q=_cb:1")
    assert res.status_code == 400
