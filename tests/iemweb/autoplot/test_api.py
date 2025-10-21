"""Excerise the imports."""

import pytest
from iemweb.autoplot import data as autoplot_data
from iemweb.autoplot.autoplot import application as autoplot_app
from iemweb.autoplot.autoplot import parser
from iemweb.autoplot.index import application as index_app
from iemweb.autoplot.meta import application as meta_app
from pyiem.exceptions import IncompleteWebRequest
from werkzeug.test import Client


def genmod():
    """Generate modules to test against."""
    for plot in autoplot_data["plots"]:
        for entry in plot["options"]:
            yield f"{entry['id']}"


def test_fourcolons():
    """Test that this raises."""
    with pytest.raises(IncompleteWebRequest):
        parser("wfo:bah::::")


def test_threecolons():
    """Test that this raises."""
    res = parser("network:WFO::wfo:::year:2025")
    assert res["network"] == "WFO"
    assert res["wfo"] == ""
    assert res["year"] == "2025"


@pytest.mark.parametrize("apid", genmod())
def test_autoplot_calls_index(apid: str):
    """Test the HTML generation via the User frontdoor."""
    c = Client(index_app)
    resp = c.get(f"?q={apid}")
    assert resp.status_code == 200


@pytest.mark.parametrize("apid", genmod())
def test_autoplot_calls_via_frontend(apid: str):
    """Just import things."""
    c = Client(meta_app)
    meta = c.get(f"?p={apid}").json
    fmts = ["png"]
    if meta["highcharts"]:
        fmts.append("js")
    if meta.get("data"):
        fmts.append("csv")
    if meta.get("raster"):
        fmts.append("geotiff")
    if meta.get("maptable"):
        fmts.append("geojson")
    for fmt in fmts:
        c = Client(autoplot_app)
        res = c.get(f"?p={apid}&fmt={fmt}&cb=1")
        # Crude check that numpy arrays are not being str rendered
        if fmt == "js":
            assert res.text.find("np.") == -1
        # 400 is Rumsfeld's knowns
        assert res.status_code in [200, 400]
