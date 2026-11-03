"""Test the metadata service."""

from iemweb.autoplot.meta import find_title, get_timing


def test_find_title():
    """Test what we get with an invalid pid."""
    assert "Unset?" in find_title(-1)


def test_simple():
    """Test the API."""
    res = get_timing(0)
    assert res == -1
