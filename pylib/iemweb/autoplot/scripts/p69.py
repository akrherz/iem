"""
The frequency of days per year that the temperature
was above/below average.  Data is shown for the current year as well, so
you should consider the representativity of that value when compared with
other years with a full year's worth of data.

<p>This app gets a bit tricky to understand the interplay between direction
and magnitude.  For example, if you pick -5 degrees as the magnitude and then
an above departure, you get the data domain of departures ranging from -5 to
positive infinity.  If you pick the absolute value departure, then you can
do the combination of departures of both sides of average.</p>
"""

from datetime import date

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot.barchart import barchart_with_top10
from iemweb.util import month2months

PDICT = {
    "high": "High Temperature",
    "low": "Low Temperature",
    "avg": "Average Temperature",
}
PDICT2 = {
    "degrees": "Degrees Fahrenheit",
    "sigma": "Sigma (1 StdDev)",
}
PDICT3 = {
    "above": "At or Above",
    "below": "Below",
    "abs_above": "Absolute Value At or Above",
    "abs_below": "Absolute Value Below",
}
PDICT4 = {"percent": "Percentage", "number": "Number"}
MDICT = {
    "all": "No Month/Season Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
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


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0000",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            options=PDICT,
            name="var",
            default="high",
            label="Which variable to plot?",
        ),
        dict(
            type="select",
            options=PDICT3,
            name="which",
            default="above",
            label="How to compare against average along with magnitude below:",
        ),
        dict(
            type="select",
            options=PDICT2,
            name="unit",
            default="degrees",
            label="How to measure departure from average:",
        ),
        dict(
            type="float",
            name="mag",
            default=0,
            label="Magnitude of departure expressed with previous:",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="select",
            name="opt",
            default="percent",
            label="Express days as percentage or number of",
            options=PDICT4,
        ),
        {
            "type": "year",
            "default": date.today().year,
            "name": "year",
            "label": "Year to highlight on chart",
        },
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    varname = ctx["var"]
    month = ctx["month"]

    yr = "year as yr"
    months = month2months(month)
    if month == "winter":
        yr = "case(when month = 12 then year + 1 else year end) as yr"

    op = "+" if ctx["which"] == "above" else "-"
    comp = ">=" if ctx["which"] in ("above", "abs_above") else "<"

    # The degrees case
    high_sql = f"high {comp} (avg_high {op} :mag)"
    low_sql = f"low {comp} (avg_low {op} :mag)"
    avg_sql = f"(high+low)/2. {comp} (avg_temp {op} :mag)"
    tt = f"{comp} {ctx['mag']}°F of Average"
    # The sigma case
    if ctx["unit"] == "sigma":
        high_sql = f"high {comp} (avg_high {op} (stddev_high * :mag))"
        low_sql = f"low {comp} (avg_low {op} (stddev_low * :mag))"
        avg_sql = f"(high+low)/2. {comp} (avg_temp {op} (stddev_temp * :mag))"
        tt = f"{comp} {ctx['mag']} Sigma of Average"
    if ctx["which"].startswith("abs"):
        # Ensure magnitude makes sense in this case
        ctx["mag"] = abs(ctx["mag"])
        if ctx["unit"] == "sigma":
            high_sql = f"abs(high - avg_high) {comp} (stddev_high * :mag)"
            low_sql = f"abs(low - avg_low) {comp} (stddev_low * :mag)"
            avg_sql = (
                f"abs((high+low)/2. - avg_temp) {comp} (stddev_temp * :mag)"
            )
            tt = f"{comp} +/- {ctx['mag']} Sigma of Average"
        else:  # degrees
            high_sql = f"abs(high - avg_high) {comp} :mag"
            low_sql = f"abs(low - avg_low) {comp} :mag"
            avg_sql = f"abs((high+low)/2. - avg_temp) {comp} :mag"
            tt = f"{comp} +/- {ctx['mag']}°F of Average"

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        WITH avgs as (
            SELECT sday,
            avg(high) as avg_high,
            stddev(high) as stddev_high,
            avg(low) as avg_low,
            stddev(low) as stddev_low,
            avg((high+low)/2.) as avg_temp,
            stddev((high+low)/2.) as stddev_temp
            from alldata WHERE
            station = :station GROUP by sday)

        SELECT {yr},
        sum(case when {high_sql} then 1 else 0 end) as high_{which},
        sum(case when {low_sql} then 1 else 0 end) as low_{which},
        sum(case when {avg_sql} then 1 else 0 end) as avg_{which},
        count(*) as days from alldata o, avgs a WHERE o.station = :station
        and o.sday = a.sday and month = ANY(:months)
        GROUP by yr ORDER by yr ASC
        """,
                yr=yr,
                which=ctx["which"],
                high_sql=high_sql,
                low_sql=low_sql,
                avg_sql=avg_sql,
            ),
            conn,
            params={
                "station": station,
                "months": months,
                "mag": ctx["mag"],
            },
            index_col="yr",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["high_freq"] = (
        df[f"high_{ctx['which']}"] / df["days"].astype("f") * 100.0
    )
    df["low_freq"] = df[f"low_{ctx['which']}"] / df["days"].astype("f") * 100.0
    df["avg_freq"] = df[f"avg_{ctx['which']}"] / df["days"].astype("f") * 100.0

    title = (
        f"{ctx['_sname']} "
        f"({df.index.values.min()}-{df.index.values.max()}) "
        f"{PDICT4[ctx['opt']]} of Days "
        f"with {PDICT[varname]} {tt}"
    )
    subtitle = (
        f"(month={month.upper()}) Using Period of Record Simple Climatology"
    )
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    suffix = f"_{ctx['which']}" if ctx["opt"] == "number" else "_freq"
    avgv = df[varname + suffix].mean()

    colorabove = "r"
    colorbelow = "b"
    if ctx["which"] == "below":
        colorabove, colorbelow = colorbelow, colorabove
    df["color"] = colorabove
    df.loc[df[varname + suffix] < avgv, "color"] = colorbelow
    if ctx["year"] in df.index:
        df.loc[ctx["year"], "color"] = "yellow"
    data = df[varname + suffix].values
    ax = barchart_with_top10(
        fig,
        df,
        f"{varname}{suffix}",
        color=df["color"],
        table_col_title="Days" if ctx["opt"] == "number" else "Freq (%)",
    )
    ax.axhline(avgv, lw=2, color="k", zorder=2)
    vv = f"Avg: {avgv:.1f}{'' if ctx['opt'] == 'number' else '%'}"
    ax.set_ylim(bottom=0)
    extra = ""
    if ctx["year"] in df.index:
        extra = (
            f" (highlighted year {ctx['year']} with value: "
            f"{data[df.index.get_loc(ctx['year'])]:.1f}"
            f"{'' if ctx['opt'] == 'number' else '%'})"
        )
    ax.set_xlabel(f"Year{extra}, {vv}")
    ax.set_ylabel(
        "Frequency [%]" if ctx["opt"] == "percent" else "Number of Days"
    )
    ax.grid(True)
    return fig, df
