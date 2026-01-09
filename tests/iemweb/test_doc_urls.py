"""Run doctests for what is found via introspection."""

import importlib
import pkgutil

import pytest
from docutils.core import publish_string
from werkzeug.test import Client


def get_mods_and_urls():
    """yield up things we can run."""
    import iemweb

    package = iemweb
    prefix = package.__name__ + "."
    for _importer, modname, _ispkg in pkgutil.walk_packages(
        package.__path__, prefix
    ):
        mod = importlib.import_module(modname)
        doc = mod.__doc__
        # Typically apache mod_rewrite is not available
        if doc is None or doc.find("NODOCTEST") > 0:
            continue
        for line in doc.split("\n"):
            if not line.strip().startswith(
                "https://mesonet.agron.iastate.edu/"
            ):
                continue
            cgi = "" if line.find("?") == -1 else line.split("?")[1]
            yield mod, f"?{cgi}"


@pytest.mark.parametrize(("mod", "cgi"), get_mods_and_urls())
def test_docutils_publish_string(mod, cgi):
    """Test that docutils can render __doc__ without any warnings."""
    # mark cgi as used so linters don't complain; it's only relevant
    # for test ids
    _ = cgi
    res = publish_string(source=mod.__doc__, writer="html").decode("utf-8")
    pos = res.find("System Message")
    if pos > 0:
        print(res[pos : pos + 100])
    assert res.find("System Message") == -1


@pytest.mark.parametrize(("mod", "cgi"), get_mods_and_urls())
def test_urls(mod, cgi):
    """Test what is found via introspection."""
    if not hasattr(mod, "application"):
        return
    c = Client(mod.application)
    res = c.get(cgi, headers={"Referer": "http://iem.local"})
    # Allow apps that redirect to check OK
    assert res.status_code in [200, 302]
