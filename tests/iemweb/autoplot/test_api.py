"""Excerise the imports."""

import pytest
from iemweb.autoplot import data as autoplot_data
from iemweb.autoplot.autoplot import application as autoplot_app
from iemweb.autoplot.autoplot import parser
from iemweb.autoplot.meta import application as meta_app
from pyiem.exceptions import IncompleteWebRequest
from werkzeug.test import Client


def genmod():
    """Generate modules to test against."""
    for plot in autoplot_data["plots"]:
        yield from plot["options"]


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


@pytest.mark.parametrize("entry", genmod())
def test_autoplot_calls_via_frontend(entry: dict):
    """Just import things."""
    c = Client(meta_app)
    meta = c.get(f"?p={entry['id']}").json
    fmts = ["png"]
    if meta["highcharts"]:
        fmts.append("js")
    if meta.get("data"):
        fmts.append("csv")
    if meta.get("raster"):
        fmts.append("geotiff")
    for fmt in fmts:
        c = Client(autoplot_app)
        res = c.get(f"?p={entry['id']}&fmt={fmt}")
        # 400 is Rumsfeld's knowns
        assert res.status_code in [200, 400]
