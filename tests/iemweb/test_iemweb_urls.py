"""Process urls.txt into mod_wsgi requests."""

import importlib
import os

import pytest
from werkzeug.test import Client


def get_mods_and_urls():
    """yield up things we can run."""
    with open(os.path.dirname(__file__) + "/urls.txt") as fh:
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
    assert res.status_code == 200
