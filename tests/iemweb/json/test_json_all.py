"""Run all the JSON services."""

import importlib
import pkgutil

import pytest
from iemweb import json as json_services
from werkzeug.test import Client


def get_services():
    """yield a list of URLs to test."""
    package_path = json_services.__path__
    for _, name, is_pkg in pkgutil.iter_modules(package_path):
        if not is_pkg:
            yield importlib.import_module(f"iemweb.json.{name}")


@pytest.mark.parametrize("service", get_services())
def test_all(service):
    """Test all apps."""
    c = Client(service.application)
    res = c.get("/")
    # 422 when a required parameter was not provided, which is fine
    assert res.status_code in [200, 422]
