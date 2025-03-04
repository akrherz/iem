"""Do apache calls for php content and ensure HTTP 200s."""

import os

import httpx
import pytest

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


def apps():
    """yield apps found in this repo."""
    for _rt, _dirs, files in os.walk("htdocs"):
        for file in files:
            fullpath = os.path.join(_rt, file)
            if fullpath.endswith((".php", ".phtml")):
                yield fullpath.replace("htdocs", "")


@pytest.mark.parametrize("app", apps())
def test_php(app):
    """Test the app."""
    if app in PUNTING:
        pytest.skip("Punting")
    resp = httpx.get(f"http://iem.local{app}", timeout=30)
    # 422 IncompleteWebRequest when there's missing CGI params
    # 301 The app could be upset about being approached via http
    # 302 redirect
    # 503 Service Temporarily Unavailable
    assert resp.status_code in [503, 422, 301, 302, 200]
