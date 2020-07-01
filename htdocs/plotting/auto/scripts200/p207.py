"""Snowfall analysis maps."""
import datetime

import numpy as np
import pandas as pd
from pyproj import Transformer
from geopandas import read_postgis, GeoDataFrame
from shapely.geometry import Polygon, Point
from scipy.interpolate import Rbf
from scipy.ndimage import zoom
from pyiem import reference
from pyiem.plot import MapPlot, nwssnow
from pyiem.util import get_autoplot_context, get_dbconn

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
    "yes": "Include any NWS COOP Reports.",
    "no": "Do not include any COOP reports.",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 60
    desc[
        "description"
    ] = """Generates an analysis map of snowfall data based on NWS Local
    Storm Reports.  This autoplot presents a number of tunables including:
    <ul>
       <li>The window of hours to look before the specified valid time to
       find Local Storm Reports (LSR).</li>
       <li>The option to attempt to inject zeros into the observations prior
       to doing an analysis.  Since the LSRs are all non-zero values, sometimes
       it is good to attempt to add zeros in to keep the reports from bleeding
       into areas that did not receive snow.</li>
       <li>You can pick which
       <a href="%s">SciPy.interpolate.Rbf</a>
       function to use.  The radius in the function shown equals the grid cell
       size used for the analysis.</li>
       <li>You can optionally include any NWS COOP reports that were processed
       by the IEM over the time period that you specified.</li>
    </ul>

    <br /><br />If you download the data for this analysis, there is a column
    called <code>%s</code> which denotes if the report was used to create the
    grid analysis.  There is a primative quality control routine that attempts
    to omit too low of reports.

    <br /><br />Having trouble with this app?  If so, please copy/paste the URL
    showing the bad image and <a href="/info/contacts.php">email it to us</a>!
    """ % (
        SCIPY,
        USEME,
    )
    now = datetime.datetime.now()
    desc["arguments"] = [
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
            default="thin_plate",
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
    ]
    return desc


def load_data(ctx, basets, endts):
    """Generate a dataframe with the data we want to analyze."""
    pgconn = get_dbconn("postgis")
    df = read_postgis(
        """SELECT state, wfo,
        max(magnitude::real) as val, ST_x(geom) as lon, ST_y(geom) as lat,
        ST_Transform(geom, 2163) as geo
        from lsrs WHERE type in ('S') and magnitude >= 0 and
        valid >= %s and valid <= %s
        GROUP by state, wfo, lon, lat, geo
        ORDER by val DESC
        """,
        pgconn,
        params=(basets, endts),
        index_col=None,
        geom_col="geo",
    )
    df[USEME] = False
    df["nwsli"] = df.index.values
    df["plotme"] = False
    df["source"] = "LSR"
    if ctx["coop"] == "no":
        return df
    # More work to do
    pgconn = get_dbconn("iem")
    days = []
    now = basets
    while now <= endts:
        days.append(now.date())
        now += datetime.timedelta(hours=24)
    df2 = read_postgis(
        """SELECT state, wfo, id as nwsli,
        sum(snow) as val, ST_x(geom) as lon, ST_y(geom) as lat,
        ST_Transform(geom, 2163) as geo
        from summary s JOIN stations t on (s.iemid = t.iemid)
        WHERE s.day in %s and t.network ~* 'COOP' and snow >= 0 and
        coop_valid >= %s and coop_valid <= %s
        GROUP by state, wfo, nwsli, lon, lat, geo
        ORDER by val DESC
        """,
        pgconn,
        params=(tuple(days), basets, endts),
        index_col=None,
        geom_col="geo",
    )
    df2[USEME] = False
    df2["plotme"] = False
    df2["source"] = "COOP"
    return pd.concat([df, df2], ignore_index=True, sort=False)


def compute_grid_bounds(ctx):
    """Figure out where to look."""
    if ctx["t"] == "state":
        if ctx["csector"] in reference.SECTORS:
            bnds = reference.SECTORS[ctx["csector"]]
            # suck
            bnds = [bnds[0], bnds[2], bnds[1], bnds[3]]
        else:
            bnds = reference.state_bounds[ctx["csector"]]
    else:
        bnds = reference.wfo_bounds[ctx["wfo"]]
    # xmin, ymin, xmax, ymax in EPSG:4326, we want meter space
    ll = T4326_2163.transform(bnds[0], bnds[1])
    ul = T4326_2163.transform(bnds[0], bnds[3])
    lr = T4326_2163.transform(bnds[2], bnds[1])
    ur = T4326_2163.transform(bnds[2], bnds[3])
    buffer = 20000.0  # km
    return [
        min(ll[0], ul[0]) - buffer,  # minx
        min(ll[1], lr[1]) - buffer,  # miny
        max(ur[0], lr[0]) + buffer,  # maxx
        max(ul[1], ur[1]) + buffer,  # maxy
    ]


def add_zeros(df, ctx):
    """ Add values of zero where we believe appropriate."""
    cellsize = ctx["sz"] * 1000.0
    newrows = []
    # loop over the grid looking for spots to add a zero
    for y in np.arange(ctx["bnds2163"][1], ctx["bnds2163"][3], cellsize):
        for x in np.arange(ctx["bnds2163"][0], ctx["bnds2163"][2], cellsize):
            # search a 2x radius for any obs
            poly = Polygon(
                [
                    [x - cellsize, y - cellsize],
                    [x - cellsize, y + cellsize],
                    [x + cellsize, y + cellsize],
                    [x + cellsize, y - cellsize],
                ]
            )
            df2 = df[df["geo"].within(poly)]
            if df2.empty:
                # Add a zero at this "point"
                (lon, lat) = T2163_4326.transform(x, y)
                if ctx["z"] != "no":
                    newrows.append(
                        {
                            "geo": Point(x, y),
                            "lon": lon,
                            "lat": lat,
                            "val": 0,
                            "nwsli": "Z%s" % (len(newrows) + 1,),
                            USEME: True,
                            "plotme": False,
                            "state": "Z",
                        }
                    )
                continue
            # For this grid cell, remove any values 20% of the max
            maxval = df.at[df2.index[0], "val"]
            df.loc[df2[df2["val"] >= (maxval * 0.2)].index, USEME] = True
            df.loc[df2[df2["val"] >= (maxval * 0.2)].index, "plotme"] = True

    return pd.concat(
        [df, GeoDataFrame(newrows, geometry="geo")],
        ignore_index=True,
        sort=False,
    )


def do_analysis(df, ctx):
    """Do the analysis finally."""
    # cull dups to prevent gridding badness
    df2 = (
        df[["geo", "val"]]
        .groupby([df["geo"].x, df["geo"].y])
        .first()
        .reset_index()
    )
    sz = ctx["sz"] * 1000.0
    xi = np.arange(ctx["bnds2163"][0], ctx["bnds2163"][2] + sz, sz)
    yi = np.arange(ctx["bnds2163"][1], ctx["bnds2163"][3] + sz, sz)
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
    # Apply a smoother
    return zoom(lons, 3), zoom(lats, 3), zoom(vals, 3)


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    if ctx["sz"] < 5:
        ctx["sz"] = 5
    if ctx["hours"] > 300:
        ctx["hours"] = 300
    endts = ctx["endts"]
    basets = endts - datetime.timedelta(hours=ctx["hours"])
    # Retrieve available obs
    df = load_data(ctx, basets, endts)
    # figure out our grid bounds
    ctx["bnds2163"] = compute_grid_bounds(ctx)
    # add zeros and QC
    df = add_zeros(df, ctx)
    # do gridding
    df2 = df[df[USEME]]
    lons, lats, vals = do_analysis(df2, ctx)

    rng = [0.01, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]
    cmap = nwssnow()
    if ctx["t"] == "cwa":
        sector = "cwa"
    else:
        sector = "state" if len(ctx["csector"]) == 2 else ctx["csector"]

    mp = MapPlot(
        sector=sector,
        state=ctx["csector"],
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        axisbg="white",
        title=("NWS Local Storm Report%s Snowfall Total Analysis")
        % (" & COOP" if ctx["coop"] == "yes" else "",),
        subtitle=(
            "%.0f reports over past %.0f hours till %s, "
            "grid size: %.0fkm, Rbf: %s"
            ""
            % (
                len(df2.index),
                ctx["hours"],
                endts.strftime("%d %b %Y %I:%M %p"),
                ctx["sz"],
                ctx["f"],
            )
        ),
    )
    if df2["val"].max() > 0 and ctx["p"] in ["both", "contour"]:
        mp.contourf(
            lons, lats, vals, rng, cmap=cmap, clip_on=(ctx["t"] != "cwa")
        )
        # Allow analysis to bleed outside the CWA per request.
        if ctx["t"] == "cwa":
            mp.draw_mask(sector="conus")
            mp.draw_cwas(linewidth=2)
    mp.drawcounties()
    if not df.empty and ctx["p"] in ["both", "plot"]:
        df2 = df[df["plotme"]]
        mp.plot_values(
            df2["lon"].values,
            df2["lat"].values,
            df2["val"].values,
            fmt="%.1f",
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
    mp.drawcities()
    return mp.fig, df.drop(["geo", "plotme"], axis=1)


if __name__ == "__main__":
    plotter(
        dict(
            csector="KS",
            endts="2020-01-29 1000",
            hours=48,
            z="plot",
            p="both",
            coop="yes",
        )
    )
