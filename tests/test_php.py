"""Smoke test PHP calls through the webserver."""

import os
from pathlib import Path

import pytest
import requests
from bs4 import BeautifulSoup

# These mapscript apps need /mesonet/data/gis/static content
PUNTING = [
    "/GIS/apps/agclimate/chill.php",
    "/GIS/apps/agclimate/gsplot.php",
    "/GIS/apps/agclimate/month.php",
    "/GIS/apps/coop/gsplot.php",
    "/GIS/apps/coop/index.php",
    "/GIS/apps/coop/plot.phtml",
    "/GIS/rby-overview.php",
    "/GIS/apps/onsite/robins.php",
    "/GIS/rad-by-year.php",
    "/GIS/radmap.php",
    "/GIS/apps/rview/compare.phtml",
    "/roads/iem.php",
    "/roads/tv.php",
    "/GIS/apps/coop/request.php",
    "/GIS/sbw-history.php",
]


def get_urls(extra):
    """yield up things we can run."""
    fn = Path(__file__).parent / f"urls{extra}.txt"
    with open(fn) as fh:
        for line in fh:
            if line.startswith("#") or line.strip() == "":
                continue
            yield line.strip()


def apps():
    """yield apps found in this repo."""
    for _rt, _dirs, files in os.walk("htdocs"):
        for file in files:
            fullpath = os.path.join(_rt, file)
            if fullpath.endswith((".php", ".phtml")):
                app = fullpath.replace("htdocs", "")
                if app in PUNTING:
                    continue
                yield app


@pytest.mark.parametrize("app", apps())
def test_php(app):
    """Test the app."""
    resp = requests.get(
        f"http://iem.local{app}", timeout=30, allow_redirects=False
    )
    # 422 IncompleteWebRequest when there's missing CGI params
    # 301 The app could be upset about being approached via http
    # 302 redirect
    # 503 Service Temporarily Unavailable
    assert resp.status_code in [503, 422, 301, 302, 200]

    # Test that the HTML generated is well formed.
    if resp.status_code == 200 and "html" in resp.headers["Content-Type"]:
        soup = BeautifulSoup(resp.text, "lxml")
        assert soup.find("title") is not None


@pytest.mark.parametrize("url", get_urls(""))
def test_php_urls(url):
    """Test the app."""
    resp = requests.get(
        f"http://iem.local{url}", timeout=30, allow_redirects=False
    )
    # 422 IncompleteWebRequest when there's missing CGI params
    # 301 The app could be upset about being approached via http
    # 302 redirect
    # 503 Service Temporarily Unavailable
    assert resp.status_code in [503, 422, 301, 302, 200]


@pytest.mark.parametrize("url", get_urls("405"))
def test_php_urls405(url):
    """Test the app."""
    resp = requests.get(
        f"http://iem.local{url}", timeout=30, allow_redirects=False
    )
    # This stinks
    assert resp.status_code in [301, 405]
