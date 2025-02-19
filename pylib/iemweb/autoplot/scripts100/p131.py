"""
This plot displays the frequency of having overcast
conditions reported by air temperature.  More specifically, this script
looks for the report of 'OVC' within the METAR sky conditions.  Many
caveats apply with the reporting changes of this over the years.
"""

from datetime import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.util import month2months

PDICT = {"CLR": "Clear (CLR)", "OVC": "Overcast (OVC)"}
MDICT = {
    "all": "No Month/Time Limit",
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
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
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
            name="var",
            default="OVC",
            options=PDICT,
            label="Overcast or Clear Sky Conditions?",
        ),
        dict(
            type="hour",
            name="hour",
            default=0,
            optional=True,
            label="Limit plot to local hour of day? (optional)",
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["zstation"]
    month = ctx["month"]
    varname = ctx["var"]
    hour = ctx.get("hour")
    months = month2months(month)

    if hour is None:
        with get_sqlalchemy_conn("asos") as conn:
            df = pd.read_sql(
                sql_helper(
                    """
                SELECT tmpf::int as t,
                SUM(case when (skyc1 = :v or skyc2 = :v or skyc3 = :v
                    or skyc4 = :v) then 1 else 0 end) as hits,
                count(*)
                from alldata where station = :station
                and tmpf is not null and
                extract(month from valid) = ANY(:months) and report_type = 3
                GROUP by t ORDER by t ASC
                """
                ),
                conn,
                params={
                    "v": varname,
                    "station": station,
                    "months": months,
                },
                index_col=None,
            )
    else:
        with get_sqlalchemy_conn("asos") as conn:
            df = pd.read_sql(
                sql_helper(
                    """
                SELECT tmpf::int as t,
                SUM(case when (skyc1 = :v or skyc2 = :v or skyc3 = :v
                    or skyc4 = :v) then 1 else 0 end) as hits,
                count(*)
                from alldata where station = :station
                and tmpf is not null and
                extract(month from valid) = ANY(:months)
                and extract(hour from ((valid +
                    '10 minutes'::interval) at time zone :tzname)) = :hour
                and report_type = 3
                GROUP by t ORDER by t ASC
                """
                ),
                conn,
                params={
                    "v": varname,
                    "station": station,
                    "months": months,
                    "tzname": ctx["_nt"].sts[station]["tzname"],
                    "hour": hour,
                },
                index_col=None,
            )
    if df.empty:
        raise NoDataFound("No data was found.")
    df["freq"] = df["hits"] / df["count"] * 100.0
    df2 = df[df["count"] > 2]
    avg = df["hits"].sum() / float(df["count"].sum()) * 100.0

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    hrlabel = "ALL"
    if hour is not None:
        ts = datetime(2000, 1, 1, hour)
        hrlabel = ts.strftime("%-I %p")
    tt = "Overcast Clouds" if varname == "OVC" else "Clear Skies"
    title = (
        f"{ctx['_sname']}\n"
        f"Frequency of {tt} by Air Temp (month={month.upper()},hour={hrlabel})"
        f" ({ab.year}-{datetime.now().year})\n"
        "(must have 3+ hourly observations at the given temperature)"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.bar(df2["t"], df2["freq"], ec="green", fc="green", width=1)
    ax.grid(True, zorder=11)
    ax.set_ylabel(f"{PDICT[varname]} Frequency [%]")
    ax.set_ylim(0, 100)
    ax.set_xlabel(r"Air Temperature $^\circ$F")
    if df2["t"].min() < 30:
        ax.axvline(32, lw=2, color="k")
        ax.text(32, -4, "32", ha="center")
    ax.axhline(avg, lw=2, color="k")
    ax.text(df2["t"].min() + 5, avg + 2, f"Avg: {avg:.1f}%")

    return fig, df
