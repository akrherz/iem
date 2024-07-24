"""Process urls.txt into mod_wsgi requests."""

import importlib
import os

import pytest
from werkzeug.test import Client


def get_mods_and_urls(extra=""):
    """yield up things we can run."""
    with open(f"{os.path.dirname(__file__)}/urls{extra}.txt") as fh:
        for line in fh:
            if line.startswith("#") or line.strip() == "":
                continue
            modname = (
                line.split("?")[0].rsplit(".", maxsplit=1)[0].replace("/", ".")
            )
            cgi = ""
            if line.find("?") > 0:
                cgi = line.split("?")[1]
            mod = importlib.import_module(f"iemweb{modname}")
            yield mod.application, f"?{cgi}"


@pytest.mark.parametrize("arg", get_mods_and_urls())
def test_urls(arg):
    """Test what urls.txt tells us to."""
    c = Client(arg[0])
    res = c.get(arg[1])
    # Allow apps that redirect to check OK
    assert res.status_code in [200, 302]


@pytest.mark.parametrize("arg", get_mods_and_urls("422"))
def test_urls422(arg):
    """Test what urls422.txt tells us to."""
    c = Client(arg[0])
    res = c.get(arg[1])
    # Allow apps that redirect to check OK
    assert res.status_code == 422
