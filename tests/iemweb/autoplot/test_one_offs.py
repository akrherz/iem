"""Test things that are hard to test directly."""

from datetime import timedelta

import responses
from iemweb.autoplot.scripts200.p221 import Params, forecast2image
from pyiem.util import utc


def test_forecast2image():
    """Walk before we run."""
    # Note that this requires the 11 UTC file
    valid = utc(2025, 9, 12, 12)
    environ = {
        "cmap": "jet",
        "w": "cwa",
        "cwa": "DMX",
        "sector": "IA",
        "valid": valid,
    }
    fhour, buf = forecast2image(Params(**environ), valid, 1)
    assert fhour == 1
    assert buf


def test_forecast2image_future():
    """Test that we don't call for a file."""
    environ = {
        "cmap": "cmap",
        "valid": utc() + timedelta(hours=3),
    }
    fhour, buf = forecast2image(
        Params(**environ), utc() + timedelta(hours=3), 1
    )
    assert fhour == 1
    assert buf is None


@responses.activate
def test_failed_archive_fetch():
    """Test that we handle a failed archive fetch gracefully."""
    responses.add(
        responses.GET, r"https://mesonet\.agron\.iastate\.edu.*", status=404
    )
    environ = {
        "valid": utc(2025, 9, 12, 11),
    }
    fhour, buf = forecast2image(Params(**environ), utc(2025, 9, 12, 11), 1)
    assert fhour == 1
    assert buf is None


def test_corrupted_grib_file():
    """Test file messed up within CI init."""
    environ = {
        "valid": utc(2024, 1, 1, 1),
    }
    fhour, buf = forecast2image(Params(**environ), utc(2024, 1, 1, 1), 1)
    assert fhour == 1
    assert buf is None
