"""
This app generates a map showing either an explicit year's first or last
date or the given percentile (observed
frequency) date over all available years of a given temperature threshold.
Sadly, this app can only plot one state's worth of data at a time.  If a
given year failed to meet the given threshold, it is not included on the
plot nor with the computed percentiles.

<br /><br />
<strong>Description of Observed Frequency:</strong> If requested, this
app will generate a plot showing the date of a given percentile for the
first/last temperature exceedance.  As a practical example of the 50th
percentile, the date plotted means that 50% of the previous years on
record experienced that temperature threshold by the given date.
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
    "spring_below": "Last Spring Date Below",
    "high_above": "First Date of Year At or Above",
    "fall_below": "First Fall Date Below",
}
PDICT = {
    "air": "Air Temperature",
    "soil": "0-10cm ERA5Land Avg Soil Temperature",
}

MONTH_DOMAIN = {
    "spring_below": list(range(1, 7)),
    "fall_below": list(range(1, 13)),
    "high_above": list(range(1, 13)),
}
SQLOPT = {
    "spring_below": " low < :t ",
    "high_above": " high >= :t ",
    "fall_below": " low < :t ",
}
YRGP = {
    "spring_below": "year",
    "high_above": "year",
    "fall_below": "winter_year",
}
ORDER = {"spring_below": "max", "fall_below": "min", "high_above": "min"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
        {
            "type": "select",
            "name": "w",
            "default": "air",
            "label": "Which Temperature:",
            "options": PDICT,
        },
        dict(type="state", name="sector", default="IA", label="Select State:"),
        dict(
            type="select",
            name="var",
            default="spring_below",
            label="Select Plot Type:",
            options=PDICT2,
        ),
        dict(
            type="select",
            name="popt",
            default="contour",
            label="Plot Display Options:",
            options=PDICT3,
        ),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Year:",
            min=1893,
        ),
        dict(
            type="int",
            name="threshold",
            default=32,
            label="Temperature Threshold (F):",
        ),
        dict(
            type="int",
            default=50,
            optional=True,
            name="p",
            label=(
                "Plot date of given observed frequency / "
                "percentiles (%): [optional]"
            ),
        ),
        dict(
            optional=True,
            type="sday",
            default=f"{today:%m%d}",
            name="sday",
            label="Plot percentiles for a given date [optional]",
        ),
        dict(
            type="year",
            default=1893,
            optional=True,
            name="syear",
            label="Inclusive start year for percentiles: [optional]",
        ),
        dict(
            type="year",
            default=today.year,
            optional=True,
            name="eyear",
            label="Inclusive end year for percentiles: [optional]",
        ),
        dict(type="cmap", name="cmap", default="BrBG", label="Color Ramp:"),
        dict(
            type="int",
            default=2,
            name="cint",
            optional=True,
            label="Contour interval in days (optional):",
        ),
    ]
    return desc


def th(val):
    """Figure out the proper ending."""
    v = val[-1]
    if v in ["0", "4", "5", "6", "7", "8", "9"]:
        return "th"
    if v in ["1"]:
        return "rst"
    if v in ["3"]:
        return "rd"
    return "nd"


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    sector = ctx["sector"]
    if len(sector) != 2:
        raise NoDataFound("Sorry, this app doesn't support multi-state plots.")
    varname = ctx["var"]
    year = ctx["year"]
    popt = ctx["popt"]
    threshold = ctx["threshold"]
    nt = NetworkTable(f"{sector}CLIMATE")
    syear = ctx.get("syear", 1893)
    eyear = ctx.get("eyear", datetime.date.today().year)
    sql = SQLOPT[varname]
    if ctx["w"] == "soil":
        sql = sql.replace("high", "soil").replace("low", "soil")
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
            -- create virtual table with winter_year included
            WITH events as (
                SELECT station, day, year, high, low,
                era5land_soilt4_avg as soil,
                case when month < 7 then year - 1 else year end as winter_year,
                extract(doy from day) as doy
                from alldata_{sector} WHERE month = ANY(:months) and
                substr(station, 3, 4) != '0000'
                and substr(station, 3, 1) not in ('C', 'D', 'T')
            )
            SELECT station, {YRGP[varname]},
            {ORDER[varname]}(
                case when {sql} then day else null end) as event,
            count(*),
            min(day) as min_day,
            max(day) as max_day
            from events
            WHERE {YRGP[varname]} >= :syear and {YRGP[varname]} <= :eyear
            GROUP by station, {YRGP[varname]}
            """
            ),
            conn,
            params={
                "months": MONTH_DOMAIN[varname],
                "t": threshold,
                "syear": syear,
                "eyear": eyear,
            },
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No data found")
    df = df[df["event"].notna()]
    df["doy"] = (df["event"] - df["min_day"]).apply(lambda x: x.days)

    basedate = datetime.date(2000, 7 if varname == "fall_below" else 1, 1)
    if ctx.get("p") is not None:
        # Remove low count stations
        df2 = df[["doy"]].groupby("station").count()
        df = df[~df.index.isin(df2[df2["doy"] < 10].index.values)]
        df2 = df[["doy"]].groupby("station").quantile(ctx["p"] / 100.0).copy()
        df2["pdate"] = df2["doy"].apply(
            lambda x: (basedate + datetime.timedelta(days=int(x))).strftime(
                "%-m/%-d"
            )
        )
        title = (
            f"{ctx['p']:.0f}{th(str(ctx['p']))} Percentile Date of "
            f"{PDICT[ctx['w']]} {PDICT2[varname]} {threshold}"
            r"$^\circ$F"
        )
        extra = (
            ", period of record: "
            f"{df[YRGP[varname]].min():.0f}-{df[YRGP[varname]].max():.0f}"
        )
    elif ctx.get("sday") is not None:
        # Compute percentiles for the given date
        df2 = df[["doy"]].groupby("station").count()
        df = df[~df.index.isin(df2[df2["doy"] < 10].index.values)]
        doy = (ctx["sday"] - basedate).days
        hits = df[df["doy"] <= doy]["doy"].groupby("station").count()
        # count again due to filtering above
        df2 = df[["doy"]].groupby("station").count()
        df2["percentile"] = (hits / df2["doy"] * 100).fillna(0)
        title = (
            f"Percentile on {ctx['sday']:%-d %b} of {PDICT2[varname]} "
            f"{threshold}"
            r"$^\circ$F"
        )
        extra = (
            ", period of record: "
            f"{df[YRGP[varname]].min():.0f}-{df[YRGP[varname]].max():.0f}"
        )
    else:
        df2 = df[df[YRGP[varname]] == year].copy()
        # Require sites have enough data
        df2 = df2[df2["count"] > (df2["count"].max() * 0.9)]
        title = f"{year} {PDICT2[varname]} {threshold}" r"$^\circ$F"
        df2["pdate"] = df2["event"].apply(lambda x: x.strftime("%-m/%-d"))
        extra = ""
    if df2.empty:
        raise NoDataFound("No Data was found")
    for station in df2.index.values:
        if station not in nt.sts:
            continue
        df2.at[station, "lat"] = nt.sts[station]["lat"]
        df2.at[station, "lon"] = nt.sts[station]["lon"]

    df2 = df2[df2["lat"].notna()]
    subtitle = f"based on NWS COOP and IEM Daily Estimates{extra}"
    if ctx["w"] == "soil":
        subtitle = "based on ERA5 Land Grid Point Estimates"
    mp = MapPlot(
        apctx=ctx,
        sector="state",
        state=ctx["sector"],
        continental_color="white",
        title=title,
        subtitle=subtitle,
        nocaption=True,
    )
    if ctx.get("p") is None and ctx.get("sday") is not None:
        mp.contourf(
            df2["lon"],
            df2["lat"],
            df2["percentile"],
            np.arange(0, 101, 10),
            cmap=ctx["cmap"],
            extend="neither",
        )
        mp.plot_values(
            df2["lon"],
            df2["lat"],
            df2["percentile"].values,
            fmt="%.0f",
            labelbuffer=5,
        )
    else:
        levs = np.linspace(
            df2["doy"].min() - 1, df2["doy"].max() + 1, 7, dtype="i"
        )
        if "cint" in ctx:
            levs = np.arange(
                df2["doy"].min() - 1,
                df2["doy"].max() + 1,
                ctx["cint"],
                dtype="i",
            )
        if popt == "contour" and (levs[-1] - levs[0]) > 5:

            def f(val):
                return (basedate + datetime.timedelta(days=int(val))).strftime(
                    "%b %-d"
                )

            levlables = list(map(f, levs))
            mp.contourf(
                df2["lon"],
                df2["lat"],
                df2["doy"],
                levs,
                clevlabels=levlables,
                cmap=ctx["cmap"],
            )
        mp.plot_values(
            df2["lon"], df2["lat"], df2["pdate"].values, labelbuffer=5
        )
    mp.drawcounties()

    return mp.fig, df[[YRGP[varname], "event", "doy"]]


if __name__ == "__main__":
    plotter({})
