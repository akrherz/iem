"""Test the metadata service."""

from iemweb.autoplot.meta import do_json, get_timing


def test_simple():
    """Test the API."""
    res = get_timing(0)
    assert res == -1
    do_json(0)
    do_json(90)
