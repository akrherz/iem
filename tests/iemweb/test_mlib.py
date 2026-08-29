"""Test mlib."""

from iemweb.mlib import rectify_wfo, unrectify_wfo


def test_rectify_wfo():
    """Test rectify_wfo()"""
    assert rectify_wfo("GUM") == "PGUM"
    assert rectify_wfo("JSJ") == "TJSJ"
    assert rectify_wfo("DMX") == "KDMX"
    assert rectify_wfo("KDMX") == "KDMX"
    assert rectify_wfo(None) is None


def test_unrectify_wfo():
    """Test unrectify_wfo()"""
    assert unrectify_wfo("PGUM") == "GUM"
    assert unrectify_wfo("TJSJ") == "JSJ"
    assert unrectify_wfo("KDMX") == "DMX"
    assert unrectify_wfo("DMX") == "DMX"
    assert unrectify_wfo(None) is None
