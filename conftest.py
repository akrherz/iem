"""Centralized Testing Stuff."""

# third party
import pytest

# This repo
from pyiem.database import get_dbconnc


@pytest.fixture()
def dbcursor(database):
    """Yield a cursor for the given database."""
    dbconn, cursor = get_dbconnc(database)
    yield cursor
    dbconn.close()
