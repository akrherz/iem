"""Test iemweb.util functions."""

from iemweb.util import month2months


def test_str_case():
    """Test our month2months function."""
    assert month2months("Jan") == [1]
    assert month2months("jan") == [1]
    assert month2months("JAN") == [1]
    assert month2months(" 01 ") == [1]
