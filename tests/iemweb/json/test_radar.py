"""Test things with the json/radar service."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from iemweb.json import radar
from pyiem.util import utc
from werkzeug.test import Client


def test_ridge_available():
    """Test we get products back for an availability request."""
    utcnow = utc(2010, 1, 1)
    with NamedTemporaryFile(suffix=".png") as tmp:
        radar.BASEDIR = Path(tmp.name).parent
        n0qfn = (
            radar.BASEDIR
            / f"{utcnow:%Y}"
            / f"{utcnow:%m}"
            / f"{utcnow:%d}"
            / "GIS"
            / "ridge"
            / "ARX"
            / "N0Q"
            / f"ARX_N0Q_{utcnow:%Y%m%d0000}.png"
        )
        Path(n0qfn).parent.mkdir(parents=True, exist_ok=True)
        with open(n0qfn, "w") as fh:
            fh.write("foo")
        c = Client(radar.application)
        # 1. List RADARs
        resp = c.get("?operation=available&start=2010-01-01T00:00Z")
        assert resp.status_code == 200
        assert any(x["id"] == "ARX" for x in resp.get_json()["radars"])
        # 2. List Products
        resp = c.get("?operation=products&start=2010-01-01T00:00Z&radar=ARX")
        assert resp.status_code == 200
        assert any(x["id"] == "N0Q" for x in resp.get_json()["products"])
        # 3. List Scans
        resp = c.get(
            "?operation=list&start=2010-01-01T00:00Z&radar=ARX&product=N0Q"
        )
        assert resp.status_code == 200
        needle = utcnow.strftime("%Y-%m-%dT%H:%MZ")
        assert any(x["ts"] == needle for x in resp.get_json()["scans"])
