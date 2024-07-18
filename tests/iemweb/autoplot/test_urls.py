"""Run a bunch of URLs through the autoplot system."""

import os

import pytest
from iemweb.autoplot.autoplot import application
from werkzeug.test import Client


def get_test_urls():
    """yield a list of URLs to test."""
    listfn = os.path.join(os.path.dirname(__file__), "urllist.txt")
    with open(listfn) as fh:
        for line in fh:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            # Do apache rewrite magic here
            line = line.replace("/plotting/auto/plot/", "")
            num, qstr = line.split("/", maxsplit=1)
            qstr, fmt = line.rsplit(".", 1)
            yield f"/?p={num}&q={qstr}&fmt={fmt}"


@pytest.mark.parametrize("url", get_test_urls())
def test_urls(url):
    """Run the test."""
    c = Client(application)
    res = c.get(url)
    assert res.status_code == 200
