"""
This tool plots the Comprehensive Climate Index (CCI) based on HRRR model
data.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pygrib
from metpy.calc import relative_humidity_from_dewpoint, wind_speed
from metpy.units import units
from pyiem.exceptions import NoDataFound
from pyiem.iemre import XAXIS, YAXIS, grb2iemre
from pyiem.meteorology import comprehensive_climate_index
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import archive_fetch, get_autoplot_context, utc

PDICT = {
    "no": "No Shade Effect",
    "yes": "Shade Effect",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    now = utc() - timedelta(hours=3)
    desc["arguments"] = [
        {
            "type": "datetime",
            "name": "valid",
            "default": now.strftime("%Y/%m/%d %H00"),
            "label": "Timestamp (UTC):",
            "min": "2014/10/11 0000",
        },
        {
            "type": "select",
            "name": "shade",
            "default": "no",
            "label": "Shade Effect:",
            "options": PDICT,
        },
        {
            "type": "csector",
            "name": "csector",
            "default": "IA",
            "label": "Select state/sector",
        },
        {
            "type": "cmap",
            "name": "cmap",
            "default": "afmhot_r",
            "label": "Color Ramp:",
        },
    ]
    return desc


def get_data(ctx: dict) -> dict:
    """Do the computation!"""
    if ctx["csector"] in ["AK", "HI"]:
        raise NoDataFound("Sector not available for this plot.")
    res = {}
    valid: datetime = ctx["valid"]
    ppath_f00 = (
        f"{valid:%Y/%m/%d}/model/hrrr/{valid:%H}/"
        f"hrrr.t{valid:%H}z.3kmf00.grib2"
    )
    ppath_f01 = (
        f"{valid:%Y/%m/%d}/model/hrrr/{valid:%H}/"
        f"hrrr.t{valid:%H}z.3kmf01.grib2"
    )
    # Get solar radiation
    with archive_fetch(ppath_f01) as testfn, pygrib.open(testfn) as grbs:
        # Eh
        srad = grb2iemre(
            grbs.select(
                name="Mean surface downward short-wave radiation flux"
            )[0]
        )

    with archive_fetch(ppath_f00) as testfn, pygrib.open(testfn) as grbs:
        u = grb2iemre(grbs.select(name="10 metre U wind component")[0])
        v = grb2iemre(grbs.select(name="10 metre V wind component")[0])
        tmpk = grb2iemre(grbs.select(name="2 metre temperature")[0])
        dwpk = grb2iemre(grbs.select(name="2 metre dewpoint temperature")[0])
        rh = relative_humidity_from_dewpoint(
            units.degK * tmpk, units.degK * dwpk
        )

    res["cci"] = comprehensive_climate_index(
        units.degK * tmpk,
        units.percent * rh,
        wind_speed(units("m/s") * u, units("m/s") * v),
        units("W/m^2") * srad,
        shade_effect=ctx["shade"] == "yes",
    )
    return res


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["valid"] = ctx["valid"].replace(tzinfo=ZoneInfo("UTC"))
    lvalid = ctx["valid"].astimezone(ZoneInfo("America/Chicago"))
    try:
        data = get_data(ctx)
    except Exception as exp:
        raise NoDataFound("No HRRR Data Found.") from exp

    sse = "With Shade" if ctx["shade"] == "yes" else "No Shade"
    mp = MapPlot(
        apctx=ctx,
        title=f"HRRR Derived Comprehensive Climate Index (CCI) [{sse}]",
        subtitle=f"Valid: {lvalid:%-d %B %Y %I:%M %p %Z}",
        stateborderwidth=3,
        nocaption=True,
    )
    cmap = get_cmap(ctx["cmap"])
    levels = list(range(25, 46, 5))
    clabels = [
        "Mild",
        "Mod",
        "Sev",
        "Extr",
        "Extr\nDng",
    ]
    x2d, y2d = np.meshgrid(XAXIS, YAXIS)
    mp.pcolormesh(
        x2d,
        y2d,
        data["cci"],
        levels,
        cmap=cmap,
        clip_on=False,
        clevlabels=clabels,
        spacing="proportional",
        extend="both",
        units="CCI",
    )
    if len(ctx["csector"]) == 2:
        mp.drawcounties()

    return mp.fig
