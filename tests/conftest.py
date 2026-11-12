"""Centralized Testing Stuff."""

from wsgiref.validate import validator

import pytest
from pyiem.database import get_dbconnc
from werkzeug.test import Client


@pytest.fixture
def dbcursor(database: str):
    """Yield a cursor for the given database."""
    dbconn, cursor = get_dbconnc(database)
    yield cursor
    cursor.close()
    dbconn.close()


@pytest.fixture
def wsgi_client(request):
    """Common WSGI client fixture."""

    class ValidatedClient(Client):
        def __init__(self, app, *args, **kwargs):
            super().__init__(validator(app), *args, **kwargs)

        def open(self, *args, **kwargs):
            kwargs["buffered"] = True
            response = super().open(*args, **kwargs)
            request.addfinalizer(response.close)
            return response

    return ValidatedClient
