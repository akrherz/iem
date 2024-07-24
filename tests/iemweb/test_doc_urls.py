"""Run doctests for what is found via introspection."""

import importlib
import pkgutil

import pytest
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
        if not hasattr(mod, "application"):
            continue
        doc = mod.__doc__
        # Typically apache mod_rewrite is not available
        if doc.find("NODOCTEST") > 0:
            continue
        for line in doc.split("\n"):
            if not line.startswith("https://mesonet.agron.iastate.edu/"):
                continue
            cgi = "" if line.find("?") == -1 else line.split("?")[1]
            yield mod.application, f"?{cgi}"


@pytest.mark.parametrize("arg", get_mods_and_urls())
def test_urls(arg):
    """Test what urls.txt tells us to."""
    c = Client(arg[0])
    res = c.get(arg[1])
    # Allow apps that redirect to check OK
    assert res.status_code in [200, 302]
