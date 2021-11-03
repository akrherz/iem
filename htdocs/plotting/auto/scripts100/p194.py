"""USDM Heatmaps and friends"""
import datetime

import numpy as np
from affine import Affine
import pandas as pd
from geopandas import read_postgis
from pyiem.plot import MapPlot
from pyiem.plot.colormaps import stretch_cmap
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.reference import LATLON

PDICT = {
    "0": "D0: Abnormally Dry",
    "1": "D1: Moderate Drought",
    "2": "D2: Severe Drought",
    "3": "D3: Extreme Drought",
    "4": "D4: Exceptional Drought",
}
PDICT2 = {"weeks": "Number of Weeks", "percent": "Percentage of Weeks"}


def proxy(mp):
    """TODO remove once pyiem updates"""
    if hasattr(mp, "panels"):
        return mp.panels[0]
    return mp.ax


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 600
    desc[
        "description"
    ] = """This application generates a heatmap of the
    frequency of a given drought classification.  The classification is the
    minimal threshold, so if a location is in D3 classification drought, it
    would count as D0, D1, D2, and D3 for this analysis.  The dates you
    specify are rectified to the previous Tuesday on which the USDM analysis
    is valid for.

    <p><strong>Caution:</strong>  This is an unofficial depiction of time
    duration of Drought Monitor classfication and due to complexities with
    how the grid analysis is done, the exact pixel location is nebulous.
    Having said that, it should be close!
    """
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="csector",
            name="csector",
            default="IA",
            label="Select state/sector to plot",
        ),
        dict(
            type="date",
            name="sdate",
            default="%s/01/01" % (today.year,),
            label="Start Date:",
            min="2000/01/04",
            max=today.strftime("%Y/%m/%d"),
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="End Date:",
            min="2000/01/04",
            max=today.strftime("%Y/%m/%d"),
        ),
        dict(
            type="select",
            name="d",
            default="0",
            options=PDICT,
            label="Select Drought Classification (at and above counted):",
        ),
        dict(
            type="select",
            name="w",
            default="percent",
            options=PDICT2,
            label="How to express time for plot:",
        ),
        dict(type="cmap", name="cmap", default="plasma", label="Color Ramp:"),
    ]
    return desc


def make_tuesday(date):
    """Make sure we back up to a tuesday"""
    offset = (date.weekday() - 1) % 7
    return date - datetime.timedelta(days=offset)


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    csector = ctx["csector"]
    sdate = make_tuesday(ctx["sdate"])
    edate = make_tuesday(ctx["edate"])
    dlevel = ctx["d"]

    griddelta = 0.1
    mp = MapPlot(
        sector=("state" if len(csector) == 2 else csector),
        state=ctx["csector"],
        title=('%s at or above "%s" %s - %s')
        % (
            PDICT2[ctx["w"]],
            PDICT[dlevel],
            sdate.strftime("%b %-d, %Y"),
            edate.strftime("%b %-d, %Y"),
        ),
        subtitle=(
            f"based on weekly US Drought Monitor Analysis, {griddelta:.2f}"
            r"$^\circ$ grid analysis"
        ),
        continentalcolor="white",
        titlefontsize=14,
        nocaption=True,
        twitter=True,
    )

    # compute the affine
    (west, east, south, north) = proxy(mp).get_extent(LATLON)
    raster = np.zeros(
        (int((north - south) / griddelta), int((east - west) / griddelta))
    )
    lons = np.arange(raster.shape[1]) * griddelta + west
    lats = np.arange(0, 0 - raster.shape[0], -1) * griddelta + north
    lats = lats[::-1]
    affine = Affine(griddelta, 0.0, west, 0.0, 0 - griddelta, north)
    # get the geopandas data
    pgconn = get_dbconn("postgis")
    df = read_postgis(
        """
    with d as (
        select valid, (ST_Dump(st_simplify(geom, 0.01))).geom from usdm where
        valid >= %s and valid <= %s and dm >= %s and
        ST_Intersects(geom, ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s %s,
         %s %s, %s %s, %s %s))'))
    )
    select valid, st_collect(geom) as the_geom from d GROUP by valid
    """,
        pgconn,
        params=(
            sdate,
            edate,
            dlevel,
            west,
            south,
            west,
            north,
            east,
            north,
            east,
            south,
            west,
            south,
        ),
        geom_col="the_geom",
    )
    if df.empty:
        raise NoDataFound("No Data Found, sorry!")
    # loop over the cached stats
    czs = CachingZonalStats(affine)
    czs.compute_gridnav(df["the_geom"], raster)
    for nav in czs.gridnav:
        if nav is None:
            continue
        grid = np.ones((nav.ysz, nav.xsz))
        grid[nav.mask] = 0.0
        jslice = slice(nav.y0, nav.y0 + nav.ysz)
        islice = slice(nav.x0, nav.x0 + nav.xsz)
        raster[jslice, islice] += grid

    maxval = 10 if np.max(raster) < 11 else np.max(raster)
    ramp = np.linspace(1, maxval + 1, 11, dtype="i")
    if ctx["w"] == "percent":
        ramp = np.arange(0, 101, 10, dtype=float)
        ramp[0] = 0.01
        ramp[-1] = 100.0
        # we add one since we are rectified to tuesdays, so we have an extra
        # week in there
        raster = raster / ((edate - sdate).days / 7.0 + 1.0) * 100.0
    # plot
    cmap = stretch_cmap(ctx["cmap"], ramp)
    cmap.set_under("white")
    cmap.set_bad("white")
    xx, yy = np.meshgrid(lons, lats)
    mp.pcolormesh(
        xx,
        yy,
        np.flipud(raster),
        ramp,
        cmap=cmap,
        units="count" if ctx["w"] == "weeks" else "Percent",
    )
    if len(csector) == 2:
        mp.drawcounties()
        mp.drawcities()

    rows = []
    for j in range(raster.shape[0]):
        for i in range(raster.shape[1]):
            rows.append(dict(lon=lons[i], lat=lats[j], value=raster[j, i]))

    return mp.fig, pd.DataFrame(rows)


if __name__ == "__main__":
    fig, _df = plotter({"w": "percent"})
    fig.savefig("/tmp/test.png")
