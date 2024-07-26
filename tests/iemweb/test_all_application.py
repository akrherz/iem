"""Smoke test anything with an application method."""

import importlib
import pkgutil

import pytest
from werkzeug.test import Client


def get_services(package_name):
    """Yield a list of modules with an 'application' attribute."""
    root = importlib.import_module(package_name)
    for _, name, is_pkg in pkgutil.iter_modules(root.__path__):
        mod = importlib.import_module(f"{package_name}.{name}")
        if is_pkg:
            for _sub in get_services(f"{package_name}.{name}"):
                yield _sub
            continue
        if hasattr(mod, "application"):
            yield mod


@pytest.mark.parametrize("service", get_services("iemweb"))
def test_all(service):
    """Test all apps."""
    c = Client(service.application)
    res = c.get("/")
    # 422 when a required parameter was not provided, which is fine
    assert res.status_code in [200, 422]
