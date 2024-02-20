"""
NCEP's Real-Time Mesoscale Analysis (RTMA) provides a fine scale hourly or in
the case of the RTMA Rapid-Update (RTMA-RU), 15 minute interval analysis of
a number of atmospheric variables.  The IEM archives a few grids for various
purposes and this app allows the generation of a plot with either the max
or min air temperature over some period of your choice.

<p><strong>Caution</strong>: The max/min values are based on hourly or 15
minute interval samples, so these will not fully capture the actual high nor
low temperature.  When the 15 minute data is available, it should certainly
do a better job than the hourly.
"""
from datetime import timedelta

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
import pygrib
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, pretty_bins
from pyiem.reference import LATLON
from pyiem.util import archive_fetch, convert_value, get_autoplot_context, utc

PDICT = {
    "max": "Maximum",
    "min": "Minimum",
}
PDICT2 = {
    "user": "User Defined",
    "fz": "Freezing Temps Mode",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    sts = utc() - timedelta(hours=26)
    ets = utc() - timedelta(hours=2)
    desc["arguments"] = [
        {
            "type": "datetime",
            "name": "sts",
            "default": sts.strftime("%Y/%m/%d %H00"),
            "label": "Start Timestamp (UTC):",
            "min": "1986/01/01 0000",
        },
        {
            "type": "datetime",
            "name": "ets",
            "default": ets.strftime("%Y/%m/%d %H00"),
            "label": (
                "End Timestamp [inclusive] (UTC), "
                "interval must be less than 4 days"
            ),
            "min": "1986/01/01 0000",
        },
        {
            "type": "select",
            "options": PDICT,
            "default": "min",
            "name": "w",
            "label": "Which statistic to compute",
        },
        {
            "type": "csector",
            "name": "csector",
            "default": "IA",
            "label": "Select state/sector",
        },
        {
            "type": "select",
            "options": PDICT2,
            "default": "user",
            "label": "Plotting mode (user defined color-ramp or freezing)",
            "name": "mode",
        },
        {
            "type": "cmap",
            "name": "cmap",
            "default": "gnuplot2",
            "label": "Color Ramp:",
        },
    ]
    return desc


def get_data(ctx):
    """Do the computation!"""
    sts = ctx["sts"]
    ets = ctx["ets"]
    ppath = (
        f"{sts:%Y/%m/%d}/model/rtma/{sts:%H}/"
        f"rtma2p5_ru.t{sts:%H%M}z.2dvaranl_ndfd.grb2"
    )
    with archive_fetch(ppath) as testfn:
        use_ru = testfn is not None
    lons = None
    lats = None
    vals = None
    func = np.minimum if ctx["w"] == "min" else np.maximum
    missing_count = 0
    total = 0
    mindt = None
    maxdt = None
    for dt in pd.date_range(sts, ets, freq="900s" if use_ru else "1h"):
        total += 1
        mydir = f"{dt:%Y/%m/%d}/model/rtma/{dt:%H}/"
        ppath = mydir + (
            f"rtma2p5_ru.t{dt:%H%M}z.2dvaranl_ndfd.grb2"
            if use_ru
            else f"rtma.t{dt:%H}z.awp2p5f000.grib2"
        )
        with archive_fetch(ppath) as fn:
            if fn is None:
                missing_count += 1
                continue
            try:
                grbs = pygrib.open(fn)
                grb = grbs.select(shortName="2t")[0]
                if lons is None:
                    lats, lons = grb.latlons()
                    vals = grb.values
                vals = func(vals, grb.values)
                grbs.close()
                if mindt is None:
                    mindt = dt
                maxdt = dt
            except Exception:
                continue
    if vals is None:
        raise NoDataFound("Failed to find any RTMA data, sorry.")
    return {
        "mindt": mindt,
        "maxdt": maxdt,
        "missing_count": missing_count,
        "total": total,
        "use_ru": use_ru,
        "lons": lons,
        "lats": lats,
        "vals": convert_value(vals, "degK", "degF"),
    }


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    if (ctx["ets"] - ctx["sts"]) > timedelta(days=4):
        ctx["ets"] = ctx["sts"] + timedelta(days=4)
    res = get_data(ctx)
    mp = MapPlot(
        apctx=ctx,
        title=(
            f"NCEP RTMA{'-RU' if res['use_ru'] else ''} {PDICT[ctx['w']]} "
            "2m Air Temperature"
        ),
        subtitle=(
            f"{res['total'] - res['missing_count']}/{res['total']} grids "
            f"found between {res['mindt']:%Y-%m-%dT%H:%MZ} and "
            f"{res['maxdt']:%Y-%m-%dT%H:%MZ}"
        ),
        stateborderwidth=3,
        nocaption=True,
    )
    if ctx["mode"] == "fz":
        # https://colorbrewer2.org/#type=diverging&scheme=RdYlBu&n=8
        # <26, 26-28, 28-30, 30-32, 32-34, 34-36, >36
        colors = (
            "#f46d43 #fdae61 #fee090 #e0f3f8 #abd9e9 #74add1 #4575b4"
        ).split()[::-1]
        cmap = mpcolors.ListedColormap(colors[1:-1])
        cmap.set_under(colors[0])
        cmap.set_over(colors[-1])
        bins = np.arange(26, 37, 2)
    else:
        # xmin, xmax, ymin, ymax
        bnds = mp.panels[0].get_extent(crs=LATLON)
        dist = np.sqrt(
            (res["lons"] - bnds[0]) ** 2 + (res["lats"] - bnds[2]) ** 2
        )
        y1, x1 = np.unravel_index(dist.argmin(), dist.shape)
        dist = np.sqrt(
            (res["lons"] - bnds[1]) ** 2 + (res["lats"] - bnds[3]) ** 2
        )
        y2, x2 = np.unravel_index(dist.argmin(), dist.shape)
        domain = res["vals"][y1:y2, x1:x2].filled(np.nan)
        ptile = np.nanpercentile(domain, [5, 95])
        bins = pretty_bins(ptile[0], ptile[1])
        cmap = ctx["cmap"]
    mp.pcolormesh(
        res["lons"],
        res["lats"],
        res["vals"],
        bins,
        cmap=cmap,
        clip_on=False,
        units=r"$^\circ$F",
        spacing="proportional",
        extend="both",
    )
    if len(ctx["csector"]) == 2:
        mp.drawcounties()

    return mp.fig


if __name__ == "__main__":
    plotter({})
