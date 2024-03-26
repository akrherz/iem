"""
This autoplot generates a map of the frequency of having at least one day
at-or-above or below a given threshold between an inclusive period of days.

<p>If you set the start date to a date greater than the end date, the effect
is to search the period including 1 January.
"""

import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT3 = {"contour": "Contour + Plot Values", "values": "Plot Values Only"}
PDICT2 = {
    "aoa": "At or Above",
    "below": "Below",
}
PDICT = {
    "high": "High Temperature",
    "low": "Low Temperature",
    "precip": "Precipitation",
    "era5land_soilt4_avg": "0-10cm ERA5Land Avg Soil Temperature",
}
UNITS = {
    "high": "F",
    "low": "F",
    "precip": "inch",
    "era5land_soilt4_avg": "F",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        {
            "type": "select",
            "name": "var",
            "default": "high",
            "label": "Which variable to plot:",
            "options": PDICT,
        },
        {
            "type": "select",
            "name": "w",
            "default": "aoa",
            "label": "Threshold Direction:",
            "options": PDICT2,
        },
        dict(type="state", name="sector", default="IA", label="Select State:"),
        dict(
            type="select",
            name="popt",
            default="contour",
            label="Plot Display Options:",
            options=PDICT3,
        ),
        {
            "type": "sday",
            "name": "sday",
            "default": "0101",
            "label": "Start Day (inclusive):",
        },
        {
            "type": "sday",
            "name": "eday",
            "default": "1231",
            "label": "End Day (inclusive):",
        },
        {
            "type": "float",
            "name": "threshold",
            "default": 100,
            "label": "Threshold Value:",
        },
        dict(
            type="year",
            default=1893,
            optional=True,
            name="syear",
            label="Limit search to years after (inclusive):",
        ),
        dict(
            type="year",
            default=datetime.date.today().year,
            optional=True,
            name="eyear",
            label="Limit search to years before (inclusive):",
        ),
        dict(type="cmap", name="cmap", default="BrBG", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    sector = ctx["sector"]
    if len(sector) != 2:
        raise NoDataFound("Sorry, this app doesn't support multi-state plots.")
    varname = ctx["var"]
    threshold = ctx["threshold"]
    if varname in ["high", "low"]:
        threshold = int(threshold)
    nt = NetworkTable(f"{sector}CLIMATE", only_online=False)
    syear = ctx.get("syear", 1893)
    eyear = ctx.get("eyear", datetime.date.today().year)
    comp = ">=" if ctx["w"] == "aoa" else "<"
    sday_limiter = "sday >= :sday and sday <= :eday"
    if ctx["sday"] > ctx["eday"]:
        sday_limiter = "(sday >= :sday or sday <= :eday)"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
            WITH events as (
                SELECT station, year,
                max(case when {varname} {comp} :t then 1 else 0 end) as hit
                from alldata_{sector} WHERE {sday_limiter} and
                year >= :syear and year <= :eyear and
                substr(station, 3, 4) != '0000'
                and substr(station, 3, 1) not in ('C', 'D', 'T')
                and {varname} is not null
                GROUP by station, year
            )
            SELECT station, count(*) as count, sum(hit) as events
            from events GROUP by station ORDER by station ASC
            """
            ),
            conn,
            params={
                "t": threshold,
                "sday": ctx["sday"].strftime("%m%d"),
                "eday": ctx["eday"].strftime("%m%d"),
                "syear": syear,
                "eyear": eyear,
            },
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No data found")
    # Require at least 50% of the years to have data
    df = df[df["count"] > (eyear - syear) / 2]
    if df.empty:
        raise NoDataFound("No data found")

    df["lat"] = np.nan
    df["lon"] = np.nan
    for station in df.index.values:
        if station not in nt.sts:
            continue
        df.at[station, "lat"] = nt.sts[station]["lat"]
        df.at[station, "lon"] = nt.sts[station]["lon"]

    df = df[df["lat"].notna()]
    df["frequency"] = df["events"] / df["count"] * 100.0
    subtitle = "based on NWS COOP and IEM Daily Estimates"
    if varname.startswith("era5land"):
        subtitle = "based on ERA5 Land Grid Point Estimates"
    if "syear" in ctx:
        subtitle += f" [{syear}-{eyear}]"
    title = (
        f"Yearly Frequency of {PDICT[varname]} "
        f"{comp} {threshold} {UNITS[varname]} between "
        f"{ctx['sday']:%-d %b} and {ctx['eday']:%-d %b}"
    )
    mp = MapPlot(
        apctx=ctx,
        sector="state",
        state=ctx["sector"],
        continental_color="white",
        title=title,
        subtitle=subtitle,
        nocaption=True,
    )
    if ctx["popt"] == "contour":
        mp.contourf(
            df["lon"],
            df["lat"],
            df["frequency"],
            np.arange(0, 101, 10),
            cmap=ctx["cmap"],
            extend="neither",
        )
    mp.plot_values(
        df["lon"],
        df["lat"],
        df["frequency"].values,
        fmt="%.0f",
        labelbuffer=5,
    )
    mp.drawcounties()

    return mp.fig, df


if __name__ == "__main__":
    plotter({})
