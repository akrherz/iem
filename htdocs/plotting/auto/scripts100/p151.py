"""
This map produces an analysis yearly averages. You
can either plot the difference between two period of years or simply the
years between the first period.  This app is meant to address the question
about changes in climate or just to produce a simple plot of yearly
averages over some period of years.
"""
import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, centered_bins, get_cmap
from pyiem.reference import SECTORS_NAME
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {
    "state": "State Level Maps (select state)",
}
PDICT.update(SECTORS_NAME)

PDICT2 = {
    "both": "Show both contour and values",
    "values": "Show just the values",
    "contour": "Show just the contour",
}
PDICT3 = {
    "total_precip": "Total Precipitation",
    "gdd": "Growing Degree Days (base=50/86)",
    "sdd": "Stress Degree Days (High > 86)",
    "avg_temp": "Average Temperature",
    "avg_high": "Average High Temperature",
    "avg_low": "Average Low Temperature",
    "days_high_above": "Days with High Temp At or Above [Threshold]",
    "days_high_below": "Days with High Temp Below [Threshold]",
    "days_low_above": "Days with Low Temp At or Above [Threshold]",
    "days_low_below": "Days with Low Temp Below [Threshold]",
}
PDICT4 = {
    "english": "English",
    "metric": "Metric",
}
UNITS = {
    "total_precip": "inch",
    "gdd": "F",
    "sdd": "F",
    "avg_temp": "F",
    "avg_high": "F",
    "avg_low": "F",
    "days_high_above": "days",
    "days_high_below": "days",
    "days_low_above": "days",
    "days_low_below": "days",
}
MUNITS = {
    "total_precip": "mm",
    "gdd": "C",
    "sdd": "C",
    "avg_temp": "C",
    "avg_high": "C",
    "avg_low": "C",
    "days_high_above": "days",
    "days_high_below": "days",
    "days_low_above": "days",
    "days_low_below": "days",
}
PRECISION = {"total_precip": 2}
MDICT = {
    "all": "Annual",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "gs": "1 May to 30 Sep",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}
OPT1 = {"diff": "Plot Difference", "p1": "Just Plot Period One Values"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="select",
            name="month",
            default="all",
            options=MDICT,
            label="Show Monthly or Annual Averages",
        ),
        dict(
            type="select",
            name="sector",
            default="state",
            options=PDICT,
            label="Select Map Region",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State to Plot (when appropriate)",
        ),
        dict(
            type="select",
            name="opt",
            options=PDICT2,
            default="both",
            label="Map Plot/Contour View Option",
        ),
        dict(
            type="select",
            name="var",
            options=PDICT3,
            default="total_precip",
            label="Which Variable to Plot",
        ),
        dict(
            type="select",
            name="r",
            options=PDICT4,
            default="english",
            label="Which Unit System to Use (GDD/SDD always english)",
        ),
        dict(
            type="float",
            name="threshold",
            default=-99,
            label="Enter threshold (where appropriate)",
        ),
        dict(
            type="select",
            options=OPT1,
            default="diff",
            name="opt1",
            label="Period plotting option",
        ),
        dict(
            type="year",
            name="p1syear",
            default=1951,
            label="Start Year (inclusive) of Period One:",
        ),
        dict(
            type="year",
            name="p1eyear",
            default=1980,
            label="End Year (inclusive) of Period One:",
        ),
        dict(
            type="year",
            name="p2syear",
            default=1981,
            label="Start Year (inclusive) of Period Two:",
        ),
        dict(
            type="year",
            name="p2eyear",
            default=2010,
            label="End Year (inclusive) of Period Two:",
        ),
        dict(
            type="cmap", name="cmap", default="seismic_r", label="Color Ramp:"
        ),
    ]
    return desc


def get_data(ctx):
    """Get the data, please."""
    state = ctx["state"]
    sector = ctx["sector"]
    threshold = ctx["threshold"]
    month = ctx["month"]
    p1syear = ctx["p1syear"]
    p1eyear = ctx["p1eyear"]
    p1years = p1eyear - p1syear + 1
    p2syear = ctx["p2syear"]
    p2eyear = ctx["p2eyear"]
    p2years = p2eyear - p2syear + 1

    mlimiter = "and month = ANY(:months)"
    if month == "all":
        mlimiter = ""
        months = list(range(1, 13))
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    elif month == "gs":
        months = [5, 6, 7, 8, 9]
    else:
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]
    table = "alldata"
    if sector == "state":
        # optimization
        table = f"alldata_{state}"
    hcol = "high"
    lcol = "low"
    pcol = "precip"
    if ctx["r"] == "metric":
        hcol = "f2c(high)"
        lcol = "f2c(low)"
        pcol = "precip * 25.4"

    sqlopts = {
        "total_precip": f"sum({pcol})",
        "gdd": "sum(gddxx(50, 86, high, low))",
        "sdd": "sum(case when high > 86 then high - 86 else 0 end)",
        "avg_temp": f"avg(({hcol}+{lcol})/2.0)",
        "avg_high": f"avg({hcol})",
        "avg_low": f"avg({lcol})",
        "days_high_above": (
            f"sum(case when {hcol}::numeric >= :t then 1 else 0 end)"
        ),
        "days_high_below": (
            f"sum(case when {hcol}::numeric < :t then 1 else 0 end)"
        ),
        "days_low_above": (
            f"sum(case when {lcol}::numeric >= :t then 1 else 0 end)"
        ),
        "days_low_below": (
            f"sum(case when {lcol}::numeric < :t then 1 else 0 end)"
        ),
    }

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
        WITH period1 as (
            SELECT station, year,
            {sqlopts[ctx['var']]} as {ctx['var']}
            from {table} WHERE year >= :syear1 and year <= :eyear1
            {mlimiter} GROUP by station, year),
        period2 as (
            SELECT station, year, 
            {sqlopts[ctx['var']]} as {ctx['var']}
            from {table} WHERE year >= :syear2 and year <= :eyear2
            {mlimiter} GROUP by station, year),
        p1agg as (
            SELECT station,
            avg({ctx['var']}) as {ctx['var']}, count(*) as count
            from period1 GROUP by station),
        p2agg as (
            SELECT station,
            avg({ctx['var']}) as {ctx['var']}, count(*) as count
            from period2 GROUP by station),
        agg as (
            SELECT p2.station,
            p2.{ctx['var']} as p2_{ctx['var']},
            p1.{ctx['var']} as p1_{ctx['var']}
            from p1agg p1 JOIN p2agg p2 on
            (p1.station = p2.station)
            WHERE p1.count >= :p1years and p2.count >= :p2years)

        SELECT ST_X(geom) as lon, ST_Y(geom) as lat,
        d.* from agg d JOIN stations t ON (d.station = t.id)
        WHERE t.network ~* 'CLIMATE'
        and substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'
        """
            ),
            conn,
            params={
                "t": threshold,
                "syear1": p1syear,
                "eyear1": p1eyear,
                "months": months,
                "syear2": p2syear,
                "eyear2": p2eyear,
                "p1years": p1years,
                "p2years": p2years,
            },
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df[ctx["var"]] = df[f"p2_{ctx['var']}"] - df[f"p1_{ctx['var']}"]
    return df


def geojson(fdict):
    """Handle GeoJSON output."""
    ctx = get_autoplot_context(fdict, get_description())
    return (get_data(ctx).drop(["lat", "lon"], axis=1)), ctx["var"]


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    df = get_data(ctx)
    state = ctx["state"]
    varname = ctx["var"]
    sector = ctx["sector"]
    threshold = ctx["threshold"]
    opt = ctx["opt"]
    month = ctx["month"]
    p1syear = ctx["p1syear"]
    p1eyear = ctx["p1eyear"]
    p2syear = ctx["p2syear"]
    p2eyear = ctx["p2eyear"]
    opt1 = ctx["opt1"]

    column = varname
    title = f"{MDICT[month]} {PDICT3[varname]}"
    title = title.replace("[Threshold]", f"{threshold:.1f}")
    if opt1 == "p1":
        column = f"p1_{varname}"
        title = f"{p1syear:.0f}-{p1eyear:.0f} {title}"
    else:
        tt = UNITS[varname] if ctx["r"] == "english" else MUNITS[varname]
        title = (
            f"{p2syear:.0f}-{p2eyear:.0f} minus {p1syear:.0f}-{p1eyear:.0f} "
            f"{title} Difference ({tt})"
        )

    # Reindex so that most extreme values are first
    df = df.reindex(df[column].abs().sort_values(ascending=False).index)
    # drop 5% most extreme events, too much?
    df2 = df.iloc[int(len(df.index) * 0.05) :]

    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=state,
        axisbg="white",
        title=title,
        subtitle="based on IEM Archives",
        titlefontsize=12,
        nocaption=True,
    )
    if opt1 == "diff":
        # Create 9 levels centered on zero
        abval = df2[column].abs().max()
        levels = centered_bins(abval)
    else:
        levels = [
            round(v, PRECISION.get(varname, 1))
            for v in np.percentile(df2[column].values, range(0, 101, 10))
        ]
    if opt in ["both", "contour"]:
        mp.contourf(
            df2["lon"].values,
            df2["lat"].values,
            df2[column].values,
            levels,
            cmap=get_cmap(ctx["cmap"]),
            units=UNITS[varname] if ctx["r"] == "english" else MUNITS[varname],
        )
    if sector == "state":
        mp.drawcounties()
    if opt in ["both", "values"]:
        mp.plot_values(
            df2["lon"].values,
            df2["lat"].values,
            df2[column].values,
            fmt=f"%.{PRECISION.get(varname, 1):.0f}f",
            labelbuffer=5,
        )

    return mp.fig, df.round(2)


if __name__ == "__main__":
    plotter({})
