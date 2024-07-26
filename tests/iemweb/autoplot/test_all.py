"""Run everything through."""

import pytest
from iemweb.autoplot.autoplot import application
from iemweb.autoplot.meta import application as meta_application
from werkzeug.test import Client


def get_test_urls():
    """yield a list of URLs to test."""
    c = Client(meta_application)
    jdata = c.get("?q=0").json
    for plot in jdata["plots"]:
        for option in plot["options"]:
            yield f"?p={option['id']}&q=_cb:1"


@pytest.mark.parametrize("url", get_test_urls())
def test_urls(url):
    """Run the test."""
    c = Client(application)
    res = c.get(url)
    assert res.status_code in [200, 400]
