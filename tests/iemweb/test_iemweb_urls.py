"""Process urls.txt into mod_wsgi requests."""

import importlib
import os

import pytest
from werkzeug.test import Client


def get_mods_and_urls(extra="") -> list[tuple[str, str]]:
    """yield up things we can run."""
    fn = f"{os.path.dirname(__file__)}/urls{extra}.txt"
    res: list[tuple[str, str]] = []
    with open(fn, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or line.strip() == "":
                continue
            modname = (
                line.replace("/cgi-bin", "")
                .split("?")[0]
                .rsplit(".", maxsplit=1)[0]
                .replace("/", ".")
            )
            cgi = ""
            if "?" in line:
                cgi = line.strip().split("?")[1]
            res.append((f"iemweb{modname}", f"?{cgi}"))
    return res


@pytest.mark.parametrize(("modname", "cgistr"), get_mods_and_urls())
def test_urls(modname: str, cgistr: str):
    """Test what urls.txt tells us to."""
    app = importlib.import_module(modname).application
    c = Client(app)
    res = c.get(cgistr)
    # Allow apps that redirect to check OK
    assert res.status_code in [200, 301, 302]


@pytest.mark.parametrize(("modname", "cgistr"), get_mods_and_urls("422"))
def test_urls422(modname: str, cgistr: str):
    """Test what urls422.txt tells us to."""
    app = importlib.import_module(modname).application
    c = Client(app)
    res = c.get(cgistr)
    assert res.status_code == 422
