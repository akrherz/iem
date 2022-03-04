"""SPC Convective Outlook Heatmaps."""
import datetime

import numpy as np
from geopandas import read_postgis
from affine import Affine
import pandas as pd
from pyiem.grid.zs import CachingZonalStats
from pyiem.plot.geoplot import MapPlot
from pyiem.plot import get_cmap
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from pyiem.exceptions import NoDataFound
from pyiem.reference import LATLON
from sqlalchemy import text


PDICT5 = {
    "yes": "YES: Draw Counties/Parishes",
    "no": "NO: Do Not Draw Counties/Parishes",
}
ISSUANCE = dict(
    (
        ("1.C.1", "Day 1 Convective @1z"),
        ("1.C.6", "Day 1 Convective @6z"),
        ("1.F.7", "Day 1 Fire Weather @7z"),
        ("1.C.13", "Day 1 Convective @13z"),
        ("1.C.16", "Day 1 Convective @16z"),
        ("1.F.17", "Day 1 Fire Weather @17z"),
        ("1.C.20", "Day 1 Convective @20z"),
        ("1.E.8", "Day 1 Excessive Rainfall @8z"),
        ("1.E.16", "Day 1 Excessive Rainfall @16z"),
        ("1.E.20", "Day 1 Excessive Rainfall @20z"),
        ("1.E.1", "Day 1 Excessive Rainfall @1z"),
        ("2.C.7", "Day 2 Convective @7z"),
        ("2.F.8", "Day 2 Fire Weather @8z"),
        ("2.C.17", "Day 2 Convective @17z"),
        ("2.F.18", "Day 2 Fire Weather @18z"),
        ("2.E.9", "Day 2 Excessive Rainfall @9z"),
        ("2.E.21", "Day 2 Excessive Rainfall @21z"),
        ("3.C.8", "Day 3 Convective @8z"),
        ("3.F.21", "Day 3 Fire Weather @21z"),
        ("3.E.9", "Day 3 Excessive Rainfall @9z"),
        ("4.C.10", "Day 4 Convective @10z"),
        ("5.C.10", "Day 5 Convective @10z"),
        ("6.C.10", "Day 6 Convective @10z"),
        ("7.C.10", "Day 7 Convective @10z"),
        ("8.C.10", "Day 8 Convective @10z"),
    )
)
OUTLOOKS = dict(
    (
        ("ANY SEVERE.0.02", "Any Severe 2% (Day 3+)"),
        ("ANY SEVERE.0.05", "Any Severe 5% (Day 3+)"),
        ("ANY SEVERE.0.15", "Any Severe 15% (Day 3+)"),
        ("ANY SEVERE.0.25", "Any Severe 25% (Day 3+)"),
        ("ANY SEVERE.0.30", "Any Severe 30% (Day 3+)"),
        ("ANY SEVERE.0.35", "Any Severe 35% (Day 3+)"),
        ("ANY SEVERE.0.45", "Any Severe 45% (Day 3+)"),
        ("ANY SEVERE.0.60", "Any Severe 60% (Day 3+)"),
        ("ANY SEVERE.SIGN", "Any Severe Significant (Day 3+)"),
        ("CATEGORICAL.TSTM", "Categorical Thunderstorm Risk (Days 1-3)"),
        ("CATEGORICAL.MRGL", "Categorical Marginal Risk (2015+) (Days 1-3)"),
        ("CATEGORICAL.SLGT", "Categorical Slight Risk (Days 1-3)"),
        ("CATEGORICAL.ENH", "Categorical Enhanced Risk (2015+) (Days 1-3)"),
        ("CATEGORICAL.MDT", "Categorical Moderate Risk (Days 1-3)"),
        ("CATEGORICAL.HIGH", "Categorical High Risk (Days 1-3)"),
        (
            "FIRE WEATHER CATEGORICAL.CRIT",
            "Categorical Critical Fire Wx (Days 1-2)",
        ),
        (
            "FIRE WEATHER CATEGORICAL.EXTM",
            "Categorical Extreme Fire Wx (Days 1-2)",
        ),
        (
            "CRITICAL FIRE WEATHER AREA.0.15",
            "Critical Fire Weather Area 15% (Days3-7)",
        ),
        ("HAIL.0.05", "Hail 5% (Days 1+2)"),
        ("HAIL.0.15", "Hail 15% (Days 1+2)"),
        ("HAIL.0.25", "Hail 25% (Days 1+2)"),
        ("HAIL.0.30", "Hail 30% (Days 1+2)"),
        ("HAIL.0.35", "Hail 35% (Days 1+2)"),
        ("HAIL.0.45", "Hail 45% (Days 1+2)"),
        ("HAIL.0.60", "Hail 60% (Days 1+2)"),
        ("HAIL.SIGN", "Hail Significant (Days 1+2)"),
        ("TORNADO.0.02", "Tornado 2% (Days 1+2)"),
        ("TORNADO.0.05", "Tornado 5% (Days 1+2)"),
        ("TORNADO.0.10", "Tornado 10% (Days 1+2)"),
        ("TORNADO.0.15", "Tornado 15% (Days 1+2)"),
        ("TORNADO.0.25", "Tornado 25% (Days 1+2)"),
        ("TORNADO.0.30", "Tornado 30% (Days 1+2)"),
        ("TORNADO.0.35", "Tornado 35% (Days 1+2)"),
        ("TORNADO.0.45", "Tornado 45% (Days 1+2)"),
        ("TORNADO.0.60", "Tornado 60% (Days 1+2)"),
        ("TORNADO.SIGN", "Tornado Significant (Days 1+2)"),
        ("WIND.0.05", "Wind 5% (Days 1+2)"),
        ("WIND.0.15", "Wind 15% (Days 1+2)"),
        ("WIND.0.25", "Wind 25% (Days 1+2)"),
        ("WIND.0.30", "Wind 30% (Days 1+2)"),
        ("WIND.0.35", "Wind 35% (Days 1+2)"),
        ("WIND.0.45", "Wind 45% (Days 1+2)"),
        ("WIND.0.60", "Wind 60% (Days 1+2)"),
        ("WIND.SIGN", "Wind Significant (Days 1+2)"),
    )
)
PDICT = {"cwa": "Plot by NWS Forecast Office", "state": "Plot by State/Sector"}
PDICT2 = {
    "avg": "Average Number of Days per Year",
    "count": "Total Number of Days",
    "lastyear": "Year of Last Issuance",
}
UNITS = {
    "avg": "days per year",
    "count": "days",
    "lastyear": "year",
}
MDICT = dict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)
GRIDWEST = -139.2
GRIDEAST = -55.1
GRIDNORTH = 54.51
GRIDSOUTH = 19.47


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """
    This application generates heatmaps of Storm Prediction Center
    convective outlooks.

    <p><strong>Major Caveat</strong>: Due to how the IEM stores the outlook
    geometries, the values presented here are for an outlook level and levels
    higher.  For example, if a location was in a moderate risk and you asked
    this app to total slight risks, the moderate risk would count toward the
    slight risk total.</p>

    <p><i class="fa fa-info"></i> This autoplot currently only considers
    outlooks since 2002.  This app is also horribly slow for reasons I have
    yet to fully debug :(</p>
    """
    desc["arguments"] = [
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="select",
            name="p",
            default="3.C.8",  # day 1 is too slow to default to :(
            options=ISSUANCE,
            label="Select SPC Product Issuance",
        ),
        dict(
            type="select",
            name="level",
            default="CATEGORICAL.SLGT",
            options=OUTLOOKS,
            label="Select outlook level:",
        ),
        dict(
            type="select",
            name="t",
            default="state",
            options=PDICT,
            label="Select plot extent type:",
        ),
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO: (ignored if plotting state)",
        ),
        dict(
            type="csector",
            name="csector",
            default="conus",
            label="Select state/sector to plot",
        ),
        dict(
            type="select",
            name="drawc",
            default="no",
            options=PDICT5,
            label="Plot County/Parish borders on maps?",
        ),
        dict(
            type="select",
            name="w",
            default="avg",
            options=PDICT2,
            label="Which metric to plot?",
        ),
        dict(
            optional=True,
            type="date",
            name="edate",
            label="Optionally limit plot to this end date:",
            min="2002/01/01",
            default=utc().strftime("%Y/%m/%d"),
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    level = ctx["level"]
    station = ctx["station"][:4]
    t = ctx["t"]
    p = ctx["p"]
    month = ctx["month"]

    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    griddelta = 0.05
    YSZ = (GRIDNORTH - GRIDSOUTH) / griddelta
    XSZ = (GRIDEAST - GRIDWEST) / griddelta

    raster = np.zeros((int(YSZ), int(XSZ)))
    lons = np.arange(GRIDWEST, GRIDEAST, griddelta)
    lats = np.arange(GRIDSOUTH, GRIDNORTH, griddelta)

    hour = int(p.split(".")[2])
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_postgis(
            text(
                """
            select product_issue, issue, expire, geom,
            extract(year from issue at time zone 'UTC') as year
            from spc_outlooks where outlook_type = :ot and day = :day and
            cycle = :hour and threshold = :t and category = :cat and
            ST_Intersects(geom,
            ST_GeomFromEWKT('SRID=4326;POLYGON((:g1 :g2, :g3 :g4,
            :g5 :g6, :g7 :g8, :g9 :g10))'))
            and extract(month from issue) in :months
            and product_issue > '2002-01-01' and
            product_issue < :edate ORDER by product_issue ASC
        """
            ),
            conn,
            params={
                "ot": p.split(".")[1],
                "day": p.split(".")[0],
                "hour": hour,
                "t": level.split(".", 1)[1],
                "cat": level.split(".")[0],
                "g1": GRIDWEST,
                "g2": GRIDSOUTH,
                "g3": GRIDWEST,
                "g4": GRIDNORTH,
                "g5": GRIDEAST,
                "g6": GRIDNORTH,
                "g7": GRIDEAST,
                "g8": GRIDSOUTH,
                "g9": GRIDWEST,
                "g10": GRIDSOUTH,
                "months": tuple(months),
                "edate": ctx.get("edate", utc() + datetime.timedelta(days=2)),
            },
            geom_col="geom",
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No results found for query")
    affine = Affine(griddelta, 0.0, GRIDWEST, 0.0, 0 - griddelta, GRIDNORTH)
    czs = CachingZonalStats(affine)
    czs.compute_gridnav(df["geom"], raster)
    for i, nav in enumerate(czs.gridnav):
        if nav is None:
            continue
        grid = np.ones((nav.ysz, nav.xsz))
        grid[nav.mask] = 0.0
        jslice = slice(nav.y0, nav.y0 + nav.ysz)
        islice = slice(nav.x0, nav.x0 + nav.xsz)
        if ctx["w"] == "lastyear":
            raster[jslice, islice] = np.max(
                [raster[jslice, islice], grid * df.loc[i]["year"]],
                axis=0,
            )
        else:
            raster[jslice, islice] += grid

    raster = np.flipud(raster)
    years = (utc() - df["issue"].min()).total_seconds() / 365.25 / 86400.0
    if ctx["w"] == "avg":
        raster = raster / years
    subtitle = (
        f"Found {len(df.index)} events for CONUS "
        f"between {df['issue'].min():%d %b %Y} and "
        f"{df['issue'].max():%d %b %Y}"
    )
    csector = ctx.pop("csector")
    if t == "cwa":
        sector = "cwa"
        subtitle = (
            f"Plotted for {ctx['_nt'].sts[station]['name']} ({station}). "
            f"{subtitle}"
        )
    else:
        sector = "state" if len(csector) == 2 else csector

    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=csector,
        cwa=(station if len(station) == 3 else station[1:]),
        axisbg="white",
        title=(
            f"{'WPC' if p.split('.')[1] == 'E' else 'SPC'} {ISSUANCE[p]} "
            f"Outlook [{MDICT[month]}] of at least "
            f"{OUTLOOKS[level].split('(')[0].strip()}"
        ),
        subtitle=f"{PDICT2[ctx['w']]}, {subtitle}",
        nocaption=True,
        twitter=True,
    )
    # Get the main axes bounds
    if t == "state" and csector == "conus":
        domain = raster
        lons, lats = np.meshgrid(lons, lats)
        df2 = pd.DataFrame()
    else:
        (west, east, south, north) = mp.panels[0].get_extent(LATLON)
        i0 = int((west - GRIDWEST) / griddelta)
        j0 = int((south - GRIDSOUTH) / griddelta)
        i1 = int((east - GRIDWEST) / griddelta)
        j1 = int((north - GRIDSOUTH) / griddelta)
        jslice = slice(j0, j1)
        islice = slice(i0, i1)
        domain = raster[jslice, islice]
        lons, lats = np.meshgrid(lons[islice], lats[jslice])
        df2 = pd.DataFrame(
            {"lat": lats.ravel(), "lon": lons.ravel(), "freq": domain.ravel()}
        )
    if ctx["w"] == "lastyear":
        domain = np.where(domain < 1, np.nan, domain)
        rng = range(int(np.nanmin(domain)), int(np.nanmax(domain)) + 2)
    elif ctx["w"] == "count":
        domain = np.where(domain < 1, np.nan, domain)
        rng = np.unique(np.linspace(1, np.nanmax(domain) + 1, 10, dtype=int))
    else:
        rng = [
            round(x, 2)
            for x in np.linspace(
                max([0.01, np.min(domain) - 0.5]), np.max(domain) + 0.1, 10
            )
        ]

    cmap = get_cmap(ctx["cmap"])
    cmap.set_bad("white")
    cmap.set_under("white")
    cmap.set_over("black")
    res = mp.pcolormesh(
        lons,
        lats,
        domain,
        rng,
        cmap=cmap,
        clip_on=False,
        units=UNITS[ctx["w"]],
        extend="both" if ctx["w"] != "lastyear" else "neither",  # dragons
    )
    # Cut down on SVG et al size
    res.set_rasterized(True)
    if ctx["drawc"] == "yes":
        mp.drawcounties()

    return mp.fig, df2


if __name__ == "__main__":
    plotter(dict(level="CATEGORICAL.SLGT"))
