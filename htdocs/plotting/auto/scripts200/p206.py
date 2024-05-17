"""Generates analysis maps of ASOS station data for a given date."""

import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_autoplot_context

PDICT = {
    "cwa": "Plot by NWS Forecast Office",
    "state": "Plot by State",
    "conus": "Plot for contiguous US",
}
PDICT2 = {
    "max_tmpf": "Max Air Temperature [F]",
    "min_tmpf": "Min Air Temperature [F]",
    "max_dwpf": "Max Dew Point Temperature [F]",
    "min_dwpf": "Min Dew Point Temperature [F]",
    "max_feel": "Max Feels Like Temperature [F]",
    "min_feel": "Min Feels Like Temperature [F]",
    "max_rh": "Max Relative Humidity [%]",
    "min_rh": "Min Relative Humidity [%]",
    "max_gust": "Peak Wind Gust [MPH]",
    "max_sknt": "Peak Sustained Wind [MPH]",
}
VARUNITS = {
    "max_tmpf": "F",
    "min_tmpf": "F",
    "max_dwpf": "F",
    "min_dwpf": "F",
    "max_feel": "F",
    "min_feel": "F",
    "max_rh": "percent",
    "min_rh": "percent",
    "max_gust": "mph",
    "max_sknt": "mph",
}
PDICT3 = {"both": "Plot and Contour Values", "plot": "Only Plot Values"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 600}
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
            type="state",
            name="state",
            default="IA",
            label="Select State: (ignored if plotting wfo)",
        ),
        dict(
            type="select",
            name="v",
            default="max_gust",
            options=PDICT2,
            label="Select statistic to plot:",
        ),
        dict(
            type="select",
            name="p",
            default="both",
            options=PDICT3,
            label="Plot or Countour values (for non interactive map):",
        ),
        dict(
            type="float",
            name="above",
            optional=True,
            default=9999,
            label="Remove any plotted values above threshold:",
        ),
        dict(
            type="float",
            name="below",
            optional=True,
            default=-9999,
            label="Remove any plotted values below threshold:",
        ),
        dict(
            type="date",
            name="day",
            default=now.strftime("%Y/%m/%d"),
            label="Date",
            min="1926/01/01",
        ),
        dict(type="cmap", name="cmap", default="viridis", label="Color Ramp:"),
    ]
    return desc


def get_df(ctx, buf=2.25):
    """Figure out what data we need to fetch here"""
    if ctx["t"] == "state":
        bnds = reference.state_bounds[ctx["state"]]
        ctx["title"] = reference.state_names[ctx["state"]]
    elif ctx["t"] == "conus":
        bnds = [
            reference.CONUS_WEST,
            reference.CONUS_SOUTH,
            reference.CONUS_EAST,
            reference.CONUS_NORTH,
        ]
        ctx["title"] = "Contiguous US"
    else:
        bnds = reference.wfo_bounds[ctx["wfo"]]
        ctx["title"] = f"NWS CWA {ctx['_sname']}"
    giswkt = "SRID=4326;POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))" % (
        bnds[0] - buf,
        bnds[1] - buf,
        bnds[0] - buf,
        bnds[3] + buf,
        bnds[2] + buf,
        bnds[3] + buf,
        bnds[2] + buf,
        bnds[1] - buf,
        bnds[0] - buf,
        bnds[1] - buf,
    )
    with get_sqlalchemy_conn("iem") as conn:
        df = gpd.read_postgis(
            """
            WITH mystation as (
                select id, st_x(geom) as lon, st_y(geom) as lat,
                state, wfo, iemid, country, geom from stations
                where network ~* 'ASOS' and
                ST_contains(ST_GeomFromEWKT(%s), geom)
            )
            SELECT s.day, s.max_tmpf, s.min_tmpf, s.max_dwpf, s.min_dwpf,
            s.min_rh, s.max_rh, s.min_feel, s.max_feel,
            max_sknt * 1.15 as max_sknt,
            max_gust * 1.15 as max_gust, t.id as station, t.lat, t.lon,
            t.wfo, t.state, t.country, t.geom from
            summary s JOIN mystation t on (s.iemid = t.iemid)
            WHERE s.day = %s
        """,
            conn,
            params=(
                giswkt,
                ctx["day"],
            ),
            geom_col="geom",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    return df[pd.notnull(df[ctx["v"]])]


def geojson(fdict):
    """GeoJSON Content."""
    ctx = get_autoplot_context(fdict, get_description())
    return (get_df(ctx).drop(columns=["lat", "lon", "day"])), ctx["v"]


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx["v"]

    df = get_df(ctx)
    if df.empty:
        raise NoDataFound("No data was found for your query")
    sector = "state" if ctx["t"] == "state" else "cwa"
    if ctx["t"] == "conus":
        sector = "conus"
    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=ctx["state"],
        cwa=(ctx["wfo"] if len(ctx["wfo"]) == 3 else ctx["wfo"][1:]),
        axisbg="white",
        title=f"{PDICT2[ctx['v']]} for {ctx['title']} on {ctx['day']}",
        nocaption=True,
        titlefontsize=16,
    )
    ramp = None
    cmap = get_cmap(ctx["cmap"])
    extend = "both"
    if varname in ["max_gust", "max_sknt"]:
        extend = "max"
        ramp = np.arange(0, 40, 4)
        ramp = np.append(ramp, np.arange(40, 80, 10))
        ramp = np.append(ramp, np.arange(80, 120, 20))
    # Data QC, cough
    if ctx.get("above"):
        df = df[df[varname] < ctx["above"]]
    if ctx.get("below"):
        df = df[df[varname] > ctx["below"]]
    if df.empty:
        raise NoDataFound("No data was found for your query")
    # with QC done, we compute ramps
    if ramp is None:
        ramp = np.linspace(
            df[varname].min() - 5, df[varname].max() + 5, 10, dtype="i"
        )

    if ctx["p"] == "both":
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df[varname].values,
            ramp,
            units=VARUNITS[varname],
            cmap=cmap,
            spacing="proportional",
            extend=extend,
        )
    if ctx["t"] == "conus":
        df2 = df[df["country"] == "US"]
    elif ctx["t"] == "state":
        df2 = df[df[ctx["t"]] == ctx[ctx["t"]]]
    else:
        df2 = df[df["wfo"] == ctx["wfo"]]

    mp.plot_values(
        df2["lon"].values,
        df2["lat"].values,
        df2[varname].values,
        "%.1f" if varname in ["max_gust", "max_sknt"] else "%.0f",
        labelbuffer=3,
    )
    if ctx["t"] != "conus":
        mp.drawcounties()
    if ctx["t"] == "cwa":
        mp.draw_cwas()

    return mp.fig, df.drop(
        columns=[
            "geom",
        ]
    )


if __name__ == "__main__":
    plotter({})
