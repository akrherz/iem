"""Test autoplots that call external services."""

import responses
from iemweb.autoplot.autoplot import application


def test_ap17(wsgi_client):
    """Test a failure found in prod."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            method=responses.GET,
            url="http://mesonet.agron.iastate.edu/api/1/daily.json",
            status=404,
        )
        c = wsgi_client(application)
        res = c.get("?p=17&q=_cb:1")
        assert res.status_code == 400
