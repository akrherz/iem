"""
Generates an analysis map of snowfall or freezing rain data
based on NWS Local Storm Reports, NWS COOP Data, and CoCoRaHS.  This autoplot
presents a number of tunables including:
<ul>
    <li>The window of hours to look before the specified valid time to
    find Local Storm Reports (LSR).</li>
    <li>The option to attempt to inject zeros into the observations prior
    to doing an analysis.  Since the LSRs are all non-zero values, sometimes
    it is good to attempt to add zeros in to keep the reports from bleeding
    into areas that did not receive snow.</li>
    <li>You can pick which
    <a href="{SCIPY}">SciPy.interpolate.Rbf</a>
    function to use.  The radius in the function shown equals the grid cell
    size used for the analysis.</li>
    <li>You can optionally include any NWS COOP reports that were processed
    by the IEM over the time period that you specified.</li>
</ul>

<br /><br />If you download the data for this analysis, there is a column
called <code>{USEME}</code> which denotes if the report was used to
create the grid analysis.  There is a primative quality control routine
that attempts to omit too low of reports.

<br /><br />Having trouble with this app?  If so, please copy/paste the URL
showing the bad image and <a href="/info/contacts.php">email it to us</a>!
"""

from datetime import datetime, timedelta

import geopandas as gpd
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot
from pyiem.plot.colormaps import nwsice, nwssnow
from pyiem.reference import EPSG
from pyiem.util import logger
from pyproj import Transformer
from scipy.interpolate import Rbf
from shapely.geometry import Point, Polygon

LOG = logger()
T4326_2163 = Transformer.from_proj(4326, 2163, always_xy=True)
T2163_4326 = Transformer.from_proj(2163, 4326, always_xy=True)
USEME = "used_for_analysis"
SCIPY = (
    "https://docs.scipy.org/doc/scipy/reference/generated/"
    "scipy.interpolate.Rbf.html"
)
PDICT = {"cwa": "Plot by NWS Forecast Office", "state": "Plot by State"}
PDICT2 = {
    "multiquadric": "multiquadraic sqrt((r/self.epsilon)**2 + 1)",
    "inverse": "inverse 1.0/sqrt((r/self.epsilon)**2 + 1)",
    "gaussian": "gaussian exp(-(r/self.epsilon)**2)",
    "linear": "linear r",
    "cubic": "cubic r**3",
    "quintic": "quintic r**5",
    "thin_plate": "thin_plate r**2 * log(r)",
}
PDICT3 = {
    "both": "Plot and Contour Values",
    "contour": "Only Contour Values",
    "plot": "Only Plot Values",
}
PDICT4 = {
    "no": "Do not attempt to inject zeros",
    "yes": "Inject zeros where necessary",
    "plot": "Inject zeros and show on plot as red 'Z'",
}
PDICT5 = {
    "yes": "Include any reports, if possible.",
    "no": "Do not include any reports.",
}
PDICT6 = {"snow": "Snowfall", "ice": "Freezing Rain / Ice Storm (LSRs Only)"}
PDICT7 = {
    "yes": "Clip Display by Plotted Geography",
    "no": "Allow sometimes extrapolation outside of plotted area",
}
PDICT8 = {
    "yes": "Overlay cities",
    "no": "Do not overlay cities",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 60}
    now = datetime.now()
    desc["gallery"] = {
        "endts": "2024-01-10 1300",
        "hours": 24,
    }
    desc["arguments"] = [
        dict(
            type="select",
            name="v",
            default="snow",
            label="Which variable to analyze?",
            options=PDICT6,
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
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO: (ignored if plotting state)",
        ),
        dict(
            type="csector",
            name="csector",
            default="IA",
            label="Select state/sector to plot",
        ),
        dict(
            type="select",
            name="p",
            default="both",
            options=PDICT3,
            label="Plot or Countour values (for non interactive map):",
        ),
        dict(
            type="datetime",
            name="endts",
            default=now.strftime("%Y/%m/%d %H%M"),
            label="Date Time (central time zone)",
            min="2006/01/01 0000",
        ),
        dict(
            type="int",
            default=12,
            label="Trailing Time Window (hours):",
            name="hours",
        ),
        dict(
            type="int",
            default=50,
            label="Grid cell size for analysis [integer] &gt;=5 (km)",
            name="sz",
            min=5,
            max=200,
        ),
        dict(
            type="select",
            options=PDICT2,
            label="Which SciPy.interpolate.Rbf function to use? r=grid size",
            default="linear",
            name="f",
        ),
        dict(
            type="select",
            options=PDICT4,
            label="Shall algorithm attempt to insert zeros into analysis?",
            default="yes",
            name="z",
        ),
        dict(
            type="select",
            options=PDICT5,
            label="Include NWS COOP reports too?",
            default="no",
            name="coop",
        ),
        {
            "type": "select",
            "options": PDICT5,
            "label": "Include CoCoRaHS reports too?",
            "default": "yes",
            "name": "cocorahs",
        },
        dict(
            type="select",
            options=PDICT7,
            label="Clip display to plotted geography?",
            default="yes",
            name="c",
        ),
        dict(
            type="select",
            options=PDICT8,
            label="Plot cities on the map?",
            default="yes",
            name="ct",
        ),
        dict(
            type="float",
            default=1,
            label="Contour line width (pixels) &lt; 10, 0 disables:",
            name="lw",
            min=0,
            max=10,
        ),
    ]
    return desc


def load_data(ctx: dict, basets: datetime, endts: datetime):
    """Generate a dataframe with the data we want to analyze."""
    with get_sqlalchemy_conn("postgis") as conn:
        df: gpd.GeoDataFrame = gpd.read_postgis(
            sql_helper(
                """SELECT state, wfo,
            max(magnitude::real) as val, ST_x(geom) as lon, ST_y(geom) as lat,
            ST_Transform(geom, 2163) as geo
            from lsrs WHERE type = :typ and magnitude >= 0 and
            valid >= :basets and valid <= :endts
            GROUP by state, wfo, lon, lat, geo
            ORDER by val DESC
            """
            ),
            conn,
            params={
                "typ": "S" if ctx["v"] == "snow" else "5",
                "basets": basets,
                "endts": endts,
            },
            index_col=None,
            geom_col="geo",
        )
    df[USEME] = True
    df["nwsli"] = df.index.values
    df["plotme"] = True
    df["source"] = "LSR"
    # Figure out which days we need to look for COOP/CoCoRaHS data, we make
    # some life choices here wanting a morning timestamp within the period
    days = [
        dt
        for dt in pd.date_range(basets.date(), endts.date())
        if basets < datetime(dt.year, dt.month, dt.day, 7) < endts
    ]
    if ctx["coop"] == "yes" and ctx["v"] != "ice":
        with get_sqlalchemy_conn("iem") as conn:
            coopdf: gpd.GeoDataFrame = gpd.read_postgis(
                sql_helper(
                    """SELECT state, wfo, id as nwsli,
                sum(snow) as val, ST_x(geom) as lon, ST_y(geom) as lat,
                ST_Transform(geom, 2163) as geo
                from summary s JOIN stations t on (s.iemid = t.iemid)
                WHERE s.day = ANY(:days)
                and t.network ~* 'COOP' and snow >= 0 and
                coop_valid >= :basets and coop_valid <= :endts
                GROUP by state, wfo, nwsli, lon, lat, geo
                ORDER by val DESC
                """
                ),
                conn,
                params={
                    "days": days,
                    "basets": basets,
                    "endts": endts,
                },
                index_col=None,
                geom_col="geo",
            )
        if not coopdf.empty:
            coopdf[USEME] = True
            coopdf["plotme"] = True
            coopdf["source"] = "COOP"
            df = pd.concat([df, coopdf], ignore_index=True, sort=False)
    if ctx["cocorahs"] == "yes" and ctx["v"] != "ice":
        with get_sqlalchemy_conn("coop") as conn:
            cocodf: gpd.GeoDataFrame = gpd.read_postgis(
                sql_helper(
                    """SELECT state, wfo, id as nwsli,
                sum(snow) as val, ST_x(geom) as lon, ST_y(geom) as lat,
                ST_Transform(geom, 2163) as geo
                from alldata_cocorahs s JOIN stations t on (s.iemid = t.iemid)
                WHERE s.day = ANY(:days)
                and t.network ~* '_COCORAHS' and snow >= 0 and
                obvalid >= :basets and obvalid <= :endts and
                ST_Contains(
                    ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 2163),
                    ST_transform(geom, 2163)
                )
                GROUP by state, wfo, nwsli, lon, lat, geo
                ORDER by val DESC
                """
                ),
                conn,
                params={
                    "days": days,
                    "basets": basets,
                    "endts": endts,
                    "minx": ctx["bnds2163"][0],
                    "miny": ctx["bnds2163"][1],
                    "maxx": ctx["bnds2163"][2],
                    "maxy": ctx["bnds2163"][3],
                },
                index_col=None,
                geom_col="geo",
            )
        if not cocodf.empty:
            cocodf[USEME] = True
            cocodf["plotme"] = True
            cocodf["source"] = "COCORAHS"
            df = pd.concat([df, cocodf], ignore_index=True, sort=False)
    return df


def compute_grid_bounds(ctx, csector):
    """Figure out where to look."""

    # Lame, we create a temp Map object to get the bounds
    if ctx["t"] == "cwa":
        sector = "cwa"
    else:
        sector = "state" if len(csector) == 2 else csector
    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        nocaption=True,
        state=csector,
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        axisbg="white",
    )
    [xmin, xmax, ymin, ymax] = mp.panels[0].get_extent(EPSG[2163])
    mp.close()

    buffer = 20000.0  # km
    return [
        xmin - buffer,  # minx
        ymin - buffer,  # miny
        xmax + buffer,  # maxx
        ymax + buffer,  # maxy
    ]


def add_zeros(df, ctx):
    """Add values of zero where we believe appropriate."""
    cellsize = ctx["sz"] * 1000.0
    newrows = []
    if ctx["z"] in ["yes", "plot"]:
        # loop over the grid looking for spots to add a zero
        for y in np.arange(
            ctx["bnds2163"][1], ctx["bnds2163"][3], cellsize * 3
        ):
            for x in np.arange(
                ctx["bnds2163"][0], ctx["bnds2163"][2], cellsize * 3
            ):
                # search a 2x radius for any obs
                poly = Polygon(
                    [
                        [x - cellsize * 1.5, y - cellsize * 1.5],
                        [x - cellsize * 1.5, y + cellsize * 1.5],
                        [x + cellsize * 1.5, y + cellsize * 1.5],
                        [x + cellsize * 1.5, y - cellsize * 1.5],
                    ]
                )
                df2 = df[df["geo"].within(poly)]
                if not df2.empty:
                    continue
                # Add a zero at this "point"
                (lon, lat) = T2163_4326.transform(x, y)
                newrows.append(
                    {
                        "geo": Point(x, y),
                        "lon": lon,
                        "lat": lat,
                        "val": 0,
                        "nwsli": f"Z{len(newrows) + 1}",
                        USEME: True,
                        "plotme": False,
                        "state": "Z",
                    }
                )
    if newrows:
        if not df.empty:
            df = pd.concat(
                (
                    df,
                    gpd.GeoDataFrame(newrows, geometry="geo", crs=EPSG[2163]),  # type: ignore
                ),
                ignore_index=True,
                sort=False,
            )
        else:
            df = gpd.GeoDataFrame(newrows, geometry="geo", crs=EPSG[2163])  # type: ignore
        # Ensure we end up with val being float
        df["val"] = pd.to_numeric(df["val"])  # type: ignore
    # compute a cell index for each row
    df["xcell"] = ((df["geo"].x - ctx["bnds2163"][0]) / cellsize).astype(int)
    df["ycell"] = ((df["geo"].y - ctx["bnds2163"][1]) / cellsize).astype(int)

    for _, gdf in df.groupby(["xcell", "ycell"]):
        if len(gdf.index) == 1:
            continue
        # Find the max value in this cell
        maxval = gdf["val"].max()
        df.loc[gdf[gdf["val"] < (maxval * 0.8)].index, USEME] = False
        df.loc[gdf[gdf["val"] < (maxval * 0.8)].index, "plotme"] = False
    return df


def do_analysis(df: pd.DataFrame, ctx: dict):
    """Do the analysis finally."""
    # cull dups to prevent gridding badness
    df2 = (
        df[["geo", "val"]]
        .groupby([df["geo"].x, df["geo"].y])
        .first()
        .reset_index()
    )
    if df2.empty:
        raise NoDataFound("No Data Found.")
    sz = ctx["sz"] * 1000.0
    # Introduce some jitter
    xi = np.arange(ctx["bnds2163"][0], ctx["bnds2163"][2] + sz, sz / 1.9)
    yi = np.arange(ctx["bnds2163"][1], ctx["bnds2163"][3] + sz, sz / 1.9)
    xi, yi = np.meshgrid(xi, yi)
    lons, lats = T2163_4326.transform(xi, yi)
    gridder = Rbf(
        df2["level_0"].values,
        df2["level_1"].values,
        df2["val"].values,
        function=ctx["f"],
    )
    vals = gridder(xi, yi)
    vals[np.isnan(vals)] = 0
    vals[vals < 0] = 0
    # Apply a smoother
    return lons, lats, vals


def prettyprint(val, decimals=1):
    """Make trace pretty."""
    if val == 0:
        return "0"
    if 0 < val < 0.1:
        return "T"
    return f"{val:.1f}" if decimals == 1 else f"{val:.2f}"


def prettyprint2(val):
    """Lazy."""
    return prettyprint(val, 2)


def plotter(ctx: dict):
    """Go"""
    ctx["sz"] = max(5, ctx["sz"])
    if ctx["hours"] > 300:
        ctx["hours"] = 300
    endts = ctx["endts"]
    basets = endts - timedelta(hours=ctx["hours"])
    # figure out our grid bounds
    csector = ctx.pop("csector")
    if ctx["t"] == "state" and len(csector) > 2:
        ctx["sz"] = max(50, ctx["sz"])
    ctx["bnds2163"] = compute_grid_bounds(ctx, csector)
    # Retrieve available obs
    df = load_data(ctx, basets, endts)
    # add zeros and QC
    df = add_zeros(df, ctx)
    df["label"] = df["val"].apply(
        prettyprint2 if ctx["v"] == "ice" else prettyprint
    )
    # do gridding
    df2 = df[df[USEME]]
    lons, lats, vals = do_analysis(df2, ctx)

    rng = [0.01, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]
    cmap = nwssnow()
    if ctx["v"] == "ice":
        rng = [0.01, 0.1, 0.25, 0.5, 0.75, 1, 2]
        cmap = nwsice()
    if ctx["t"] == "cwa":
        sector = "cwa"
    else:
        sector = "state" if len(csector) == 2 else csector

    _t = " & COOP" if ctx["coop"] == "yes" else ""
    _t += " & CoCoRaHS" if ctx["cocorahs"] == "yes" else ""
    title = f"NWS Local Storm Report{_t} Snowfall Total Analysis"
    if ctx["v"] == "ice":
        title = "NWS Local Storm Reports of Freezing Rain + Ice"
    obcnt = len(df2[df2["state"] != "Z"].index)
    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        nocaption=True,
        state=csector,
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        axisbg="white",
        title=title,
        subtitle=(
            f"{obcnt:.0f} reports over past {ctx['hours']:.0f} hours "
            f"till {endts:%d %b %Y %I:%M %p}, "
            f"grid size: {ctx['sz']:.0f}km, Rbf: {ctx['f']}"
        ),
    )
    if df2["val"].max() > 0 and ctx["p"] in ["both", "contour"]:
        mp.contourf(
            lons,
            lats,
            vals,
            rng,
            cmap=cmap,
            clip_on=(ctx["c"] == "yes"),
            linewidths=ctx["lw"],
            spacing="proportional",
        )
        # Allow analysis to bleed outside the CWA per request.
        if ctx["t"] == "cwa":
            mp.draw_mask(sector="conus")
            mp.draw_cwas(linewidth=2)
    if sector not in ["conus", "midwest"] and not (
        ctx["t"] == "state" and len(csector) > 2
    ):
        mp.drawcounties()
    if ctx["ct"] == "yes":
        mp.drawcities(isolated=True, textoutlinewidth=0)
    if not df.empty and ctx["p"] in ["both", "plot"]:
        df2 = df[df["plotme"]]
        mp.plot_values(
            df2["lon"].values,
            df2["lat"].values,
            df2["label"].values,
            fmt="%s",
            labelbuffer=2,
        )
    if ctx["z"] == "plot":
        df2 = df[df["state"] == "Z"]
        if not df2.empty:
            mp.plot_values(
                df2["lon"].values,
                df2["lat"].values,
                df2["state"].values,
                fmt="%s",
                color="#FF0000",
                labelbuffer=0,
            )
    return mp.fig, df.drop(["geo", "plotme"], axis=1)
