"""Test any mod_wsgi apps in this repo."""

import os

import pytest
import requests


def apps():
    """yield apps found in this repo."""
    # Find any files in htdocs and cgi-bin named *.py
    # that are not named __init__.py
    # and import them as modules.
    # Then yield them as apps.
    # This will allow us to test any mod_wsgi apps
    # in this repo.
    for rt, _dirs, files in os.walk("."):
        if rt.startswith("./htdocs/plotting/auto/scripts"):
            continue
        if rt.startswith(("./htdocs", "./cgi-bin")):
            for file in files:
                fullpath = os.path.join(rt, file)
                if fullpath.endswith(".py") and fullpath != "__init__.py":
                    yield fullpath.replace("/htdocs", "")[1:]  # drop the .


@pytest.mark.parametrize("app", list(apps()))
def test_app(app):
    """Test the app."""
    resp = requests.get(f"http://iem.local{app}", timeout=30)
    # 422 IncompleteWebRequest when there's missing CGI params
    # 301 The app could be upset about being approached via http
    # 503 some of apps are now proxied, so alas
    assert resp.status_code in [422, 301, 200, 503]
