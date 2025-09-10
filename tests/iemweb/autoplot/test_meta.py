"""Test the metadata service."""

from iemweb.autoplot.meta import get_metadict, get_timing


def test_simple():
    """Test the API."""
    res = get_timing(0)
    assert res == -1
    get_metadict(0)
    get_metadict(90)
