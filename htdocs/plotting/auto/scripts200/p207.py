"""Snowfall analysis maps."""
import datetime

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from scipy.interpolate import Rbf
from pyiem import reference
from pyiem.plot import MapPlot, nwssnow
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {"cwa": "Plot by NWS Forecast Office", "state": "Plot by State"}
PDICT3 = {
    "both": "Plot and Contour Values",
    "contour": "Only Contour Values",
    "plot": "Only Plot Values",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 60
    desc[
        "description"
    ] = """Generates an analysis map of snowfall data based on NWS Local
    Storm Reports."""
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
    ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    pgconn = get_dbconn("postgis")
    endts = ctx["endts"]
    csector = ctx["csector"]
    basets = endts - datetime.timedelta(hours=ctx["hours"])

    df = read_sql(
        """SELECT state, wfo,
        max(magnitude) as val, ST_x(geom) as lon, ST_y(geom) as lat
        from lsrs WHERE type in ('S') and magnitude >= 0 and
        valid > %s and valid < %s GROUP by state, wfo, lon, lat
        """,
        pgconn,
        params=(basets, endts),
        index_col=None,
    )
    df.sort_values(by="val", ascending=False, inplace=True)
    df["useme"] = False
    df["plotme"] = False

    if ctx["t"] == "state":
        if csector in reference.SECTORS:
            bnds = reference.SECTORS[csector]
            # suck
            bnds = [bnds[0], bnds[2], bnds[1], bnds[3]]
        else:
            df.loc[df["state"] == csector, "plotme"] = True
            bnds = reference.state_bounds[csector]
    else:
        df.loc[df["wfo"] == ctx["wfo"], "plotme"] = True
        bnds = reference.wfo_bounds[ctx["wfo"]]

    # Pick a cell size that is roughly 10% of the domain size
    cellsize = (bnds[3] - bnds[1]) * 0.1
    newrows = []
    for lat in np.arange(bnds[1], bnds[3], cellsize):
        for lon in np.arange(bnds[0], bnds[2], cellsize):
            # Look around this box at 1x
            df2 = df[
                (df["lat"] >= (lat - cellsize))
                & (df["lat"] < (lat + cellsize))
                & (df["lon"] >= (lon - cellsize))
                & (df["lon"] < (lon + cellsize))
            ]
            if df2.empty:
                # If nothing was found, check 2x
                df3 = df[
                    (df["lat"] >= (lat - cellsize * 2.0))
                    & (df["lat"] < (lat + cellsize * 2.0))
                    & (df["lon"] >= (lon - cellsize * 2.0))
                    & (df["lon"] < (lon + cellsize * 2.0))
                ]
                if df3.empty:
                    # If nothing found, place a zero here
                    newrows.append(
                        {
                            "lon": lon,
                            "lat": lat,
                            "val": 0,
                            "useme": True,
                            "plotme": False,
                            "state": "NA",
                        }
                    )
                continue
            maxval = df.at[df2.index[0], "val"]
            df.loc[df2[df2["val"] > (maxval * 0.8)].index, "useme"] = True

    dfall = pd.concat(
        [df, pd.DataFrame(newrows)], ignore_index=True, sort=False
    )
    df2 = dfall[dfall["useme"]]
    xi = np.arange(bnds[0] - 1.0, bnds[2] + 1.0, cellsize)
    yi = np.arange(bnds[1] - 1.0, bnds[3] + 1.0, cellsize)
    xi, yi = np.meshgrid(xi, yi)
    gridder = Rbf(
        df2["lon"].values,
        df2["lat"].values,
        pd.to_numeric(df2["val"].values, errors="ignore"),
        function="thin_plate",
    )
    vals = gridder(xi, yi)
    vals[np.isnan(vals)] = 0

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
        title="Local Storm Report Snowfall Total Analysis",
        subtitle=(
            "Reports past %.0f hours: %s"
            "" % (ctx["hours"], endts.strftime("%d %b %Y %I:%M %p"))
        ),
    )
    if df2["val"].max() > 0 and ctx["p"] in ["both", "contour"]:
        mp.contourf(xi, yi, vals, rng, cmap=cmap, clip_on=(ctx["t"] != "cwa"))
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
    mp.drawcities()

    return mp.fig, df


if __name__ == "__main__":
    plotter(dict(wfo="BOU", t="cwa"))
