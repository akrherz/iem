"""Test things that are hard to test directly."""

from datetime import timedelta

from iemweb.autoplot.scripts200.p221 import forecast2image
from pyiem.plot import get_cmap
from pyiem.util import utc
from pytest_httpx import HTTPXMock


def test_forecast2image():
    """Walk before we run."""
    environ = {
        "cmap": get_cmap("jet"),
        "w": "cwa",
        "cwa": "DMX",
        "sector": "IA",
    }
    fhour, buf = forecast2image(environ, utc(2025, 9, 12, 11), 1)
    assert fhour == 1
    assert buf


def test_forecast2image_future():
    """Test that we don't call for a file."""
    fhour, buf = forecast2image({}, utc() + timedelta(hours=3), 1)
    assert fhour == 1
    assert buf is None


def test_failed_archive_fetch(httpx_mock: HTTPXMock):
    """Test that we handle a failed archive fetch gracefully."""
    httpx_mock.add_response(status_code=404)
    fhour, buf = forecast2image({}, utc(2025, 9, 12, 11), 1)
    assert fhour == 1
    assert buf is None


def test_corrupted_grib_file():
    """Test file messed up within CI init."""
    fhour, buf = forecast2image({}, utc(2024, 1, 1, 1), 1)
    assert fhour == 1
    assert buf is None
