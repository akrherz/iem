"""
Based on IEM archives of METAR reports, this
application produces the hourly frequency of a temperature at or
above or below a temperature thresold.
"""

import calendar

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

PDICT = {
    "above": "At or Above Temperature",
    "below": "Below Temperature",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(type="month", name="month", default=7, label="Month:"),
        dict(
            type="int",
            name="t",
            default=80,
            label="Temperature Threshold (F):",
        ),
        dict(
            type="select",
            name="dir",
            default="above",
            label="Threshold Option:",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    month = int(ctx["month"])
    thres = ctx["t"]
    mydir = ctx["dir"]

    tzname = ctx["_nt"].sts[station]["tzname"]
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
        WITH data as (
            SELECT valid at time zone %s  + '10 minutes'::interval as v, tmpf
            from alldata where station = %s and tmpf > -90 and tmpf < 150
            and extract(month from valid) = %s and report_type = 3)

        SELECT extract(hour from v) as hour,
        min(v) as min_valid, max(v) as max_valid,
        sum(case when tmpf::int < %s THEN 1 ELSE 0 END) as below,
        sum(case when tmpf::int >= %s THEN 1 ELSE 0 END) as above,
        count(*) from data
        GROUP by hour ORDER by hour ASC
        """,
            conn,
            params=(tzname, station, month, thres, thres),
            index_col="hour",
        )
    if df.empty:
        raise NoDataFound("No data found.")

    df["below_freq"] = df["below"].values.astype("f") / df["count"] * 100.0
    df["above_freq"] = df["above"].values.astype("f") / df["count"] * 100.0

    freq = df[mydir + "_freq"].values
    hours = df.index.values
    title = (
        f"({df['min_valid'].min().year} - {df['max_valid'].max().year}) "
        f"{ctx['_sname']}\n"
        f"Frequency of {calendar.month_name[month]} Hour, {PDICT[mydir]}: "
        f"{thres}"
        r"$^\circ$F"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)
    bars = ax.bar(hours, freq, fc="blue", align="center")
    for i, mybar in enumerate(bars):
        ax.text(
            i,
            mybar.get_height() + 3,
            f"{mybar.get_height():.0f}",
            ha="center",
            fontsize=10,
        )
    ax.set_xticks(range(0, 25, 3))
    ax.set_xticklabels(
        ["Mid", "3 AM", "6 AM", "9 AM", "Noon", "3 PM", "6 PM", "9 PM", "Mid"]
    )
    ax.grid(True)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Frequency [%]")
    ax.set_xlabel(f"Hour Timezone: {tzname}")
    ax.set_xlim(-0.5, 23.5)

    return fig, df
