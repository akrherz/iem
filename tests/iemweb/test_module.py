"""Test iemweb module."""

import iemweb


def test_api():
    """Can we import the iemweb module?"""
    assert iemweb.__version__ is not None
