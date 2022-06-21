"""Generalized mapper of AZOS data"""
import datetime
import os

import numpy as np
import pygrib
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.util import get_autoplot_context, utc, mm2inch
from pyiem.exceptions import NoDataFound

PDICT = {"120": "Five Day", "168": "Seven Day"}
PDICT2 = {"0": "0z (7 PM CDT)", "12": "12z (7 AM CDT)"}
PDICT3 = {
    "both": "Plot both USDM + WPC Forecast",
    "wpc": "Plot just WPC Forecast",
}
PDICT4 = {
    "auto": "Auto-scale",
    "10": "10 inch max",
    "7": "7 inch max",
    "3.5": "3.5 inch max",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = False
    desc["cache"] = 600
    desc[
        "description"
    ] = """Generates a map of WPC Quantitative Precipitation
    Forecast (QPF) and most recent US Drought Monitor to the date choosen to
    plot the WPC forecast."""
    utcnow = datetime.datetime.utcnow()
    desc["arguments"] = [
        dict(
            type="csector",
            name="csector",
            default="IA",
            label="Select state/sector to plot",
        ),
        dict(
            type="date",
            name="date",
            default=utcnow.strftime("%Y/%m/%d"),
            label="Select WPC Issuance Date:",
            min="2018/05/11",
            max=utcnow.strftime("%Y/%m/%d"),
        ),
        dict(
            type="select",
            name="z",
            default="0",
            options=PDICT2,
            label="Select WPC Issuance Time",
        ),
        dict(
            type="select",
            name="f",
            default="120",
            options=PDICT,
            label="Select WPC Forecast Period:",
        ),
        dict(
            type="select",
            name="opt",
            default="both",
            options=PDICT3,
            label="Plotting Options:",
        ),
        dict(
            type="select",
            name="scale",
            default="auto",
            options=PDICT4,
            label="WPC Plotting Max Value for Color Ramp:",
        ),
        dict(
            type="cmap", name="cmap", default="gist_ncar", label="Color Ramp:"
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    date = ctx["date"]
    z = ctx["z"]
    period = ctx["f"]
    scale = ctx["scale"]
    valid = utc(date.year, date.month, date.day, int(z))
    gribfn = valid.strftime(
        (
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/wpc/"
            "p" + period + "m_%Y%m%d%Hf" + period + ".grb"
        )
    )
    if not os.path.isfile(gribfn):
        raise NoDataFound(f"gribfn {gribfn} missing")

    grbs = pygrib.open(gribfn)
    grb = grbs[1]
    precip = mm2inch(grb.values)
    lats, lons = grb.latlons()

    title = (
        f"Weather Prediction Center {PDICT[period]} "
        "Quantitative Precipitation Forecast"
    )
    _t = "US Drought Monitor Overlaid, " if ctx["opt"] == "both" else ""
    subtitle = (
        f"{_t}WPC Forecast {valid:%d %b %Y %H} UTC to "
        f"{(valid + datetime.timedelta(hours=int(period))):%d %b %Y %H} UTC"
    )
    mp = MapPlot(
        apctx=ctx,
        title=title,
        subtitle=subtitle,
        continentalcolor="white",
        titlefontsize=16,
        nocaption=True,
    )
    cmap = get_cmap(ctx["cmap"])
    cmap.set_under("#EEEEEE")
    cmap.set_over("black")
    if scale == "auto":
        levs = pretty_bins(0, np.max(precip))
        levs[0] = 0.01
    elif scale == "10":
        levs = np.arange(0, 10.1, 1.0)
        levs[0] = 0.01
    elif scale == "7":
        levs = np.arange(0, 7.1, 0.5)
        levs[0] = 0.01
    elif scale == "3.5":
        levs = np.arange(0, 3.6, 0.25)
        levs[0] = 0.01
    mp.pcolormesh(
        lons,
        lats,
        precip,
        levs,
        cmap=cmap,
        units="inch",
        clip_on=(ctx["csector"] == "iailin"),
    )
    if ctx["opt"] == "both":
        mp.draw_usdm(valid=valid, filled=False, hatched=True)
    if ctx["csector"] == "iailin":
        mp.drawcounties()

    return mp.fig


if __name__ == "__main__":
    plotter({})
