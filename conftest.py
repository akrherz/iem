"""Centralized Testing Stuff."""

import pytest
from pyiem.database import get_dbconnc


@pytest.fixture
def dbcursor(database):
    """Yield a cursor for the given database."""
    dbconn, cursor = get_dbconnc(database)
    yield cursor
    cursor.close()
    dbconn.close()
