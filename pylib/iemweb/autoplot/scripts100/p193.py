"""
Generates a map of WPC Quantitative Precipitation
Forecast (QPF) and most recent US Drought Monitor to the date choosen to
plot the WPC forecast
"""

import datetime as dt
from datetime import timedelta
from typing import Annotated

import numpy as np
import pygrib
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.util import archive_fetch, mm2inch, utc

from iemweb.autoplot.description import (
    CmapArg,
    CSectorArg,
    DateArg,
    PlotDescription,
    SelectArg,
)
from iemweb.autoplot.params import AutoplotParams

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


class Params(AutoplotParams):
    """Request parameters."""

    csector: Annotated[
        str, CSectorArg(label="Select state/sector to plot")
    ] = "IA"
    date: Annotated[
        dt.date,
        DateArg(
            label="Select WPC Issuance Date:",
            min="2018/05/11",
            max=lambda: utc().strftime("%Y/%m/%d"),
            default=lambda: utc().strftime("%Y/%m/%d"),
        ),
    ]
    z: Annotated[
        str, SelectArg(options=PDICT2, label="Select WPC Issuance Time")
    ] = "0"
    f: Annotated[
        str, SelectArg(options=PDICT, label="Select WPC Forecast Period:")
    ] = "120"
    opt: Annotated[
        str, SelectArg(options=PDICT3, label="Plotting Options:")
    ] = "both"
    scale: Annotated[
        str,
        SelectArg(
            options=PDICT4, label="WPC Plotting Max Value for Color Ramp:"
        ),
    ] = "auto"
    cmap: Annotated[str, CmapArg(label="Color Ramp:")] = "gist_ncar"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=False, cache=600
    )


def plotter(ctx: Params):
    """Go"""
    dt = ctx.date
    z = ctx.z
    period = ctx.f
    scale = ctx.scale
    valid = utc(dt.year, dt.month, dt.day, int(z))
    with archive_fetch(
        valid.strftime(f"%Y/%m/%d/model/wpc/p{period}m_%Y%m%d%Hf{period}.grb")
    ) as gribfn:
        if gribfn is None:
            raise NoDataFound(f"gribfn {gribfn} missing")
        with pygrib.open(gribfn) as grbs:
            grb = grbs[1]
            lats, lons = grb.latlons()
            precip = mm2inch(grb.values)

    title = (
        f"Weather Prediction Center {PDICT[period]} "
        "Quantitative Precipitation Forecast"
    )
    _t = "US Drought Monitor Overlaid, " if ctx.opt == "both" else ""
    subtitle = (
        f"{_t}WPC Forecast {valid:%d %b %Y %H} UTC to "
        f"{(valid + timedelta(hours=int(period))):%d %b %Y %H} UTC"
    )
    mp = MapPlot(
        apctx=ctx,
        title=title,
        subtitle=subtitle,
        continentalcolor="white",
        titlefontsize=16,
        nocaption=True,
    )
    cmap = get_cmap(ctx.cmap).with_extremes(under="#EEEEEE", over="k")
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
        clip_on=(ctx.csector == "iailin"),
    )
    if ctx.opt == "both":
        mp.draw_usdm(valid=valid, filled=False, hatched=True)
    if ctx.csector == "iailin":
        mp.drawcounties()

    return mp.fig
