"""
This plot produces the daily frequency of
a given criterion being meet for a station and month of your choice. The
number labeled above each bar is the actual number of years.
"""

import calendar

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

from iemweb.autoplot import ARG_STATION

PDICT = {
    "precip": "Daily Precipitation",
    "snow": "Daily Snowfall",
    "snowd": "Daily Snow Depth",
    "high": "High Temperature",
    "low": "Low Temperature",
}

PDICT2 = {"above": "At or Above Threshold", "below": "Below Threshold"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(type="month", name="month", default=9, label="Which Month:"),
        dict(
            type="select",
            name="var",
            default="high",
            label="Which Variable:",
            options=PDICT,
        ),
        dict(
            type="text",
            name="thres",
            default="90",
            label="Threshold (F or inch):",
        ),
        dict(
            type="select",
            name="dir",
            default="above",
            label="Threshold Direction:",
            options=PDICT2,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]
    month = ctx["month"]
    threshold = float(ctx["thres"])
    if PDICT.get(varname) is None:
        raise NoDataFound("No Data Found.")
    drct = ctx["dir"]
    if PDICT2.get(drct) is None:
        raise NoDataFound("No Data Found.")
    operator = ">=" if drct == "above" else "<"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
            SELECT sday,
            sum(case when {varname}::numeric {operator} %s then 1 else 0 end)
            as hit,
            count(*) as total
            from alldata WHERE station = %s and month = %s
            GROUP by sday ORDER by sday ASC
            """,
            conn,
            params=(threshold, station, month),
            index_col="sday",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["freq"] = df["hit"] / df["total"] * 100.0

    vv = df["hit"].sum() / float(df["total"].sum()) * len(df.index)
    title = (
        f"{ctx['_sname']} :: {PDICT.get(varname)} {PDICT2.get(drct)} "
        f"{threshold}\n"
        f"during {calendar.month_name[month]} "
        f"(Avg: {vv:.2f} days/year)"
    )
    fig, ax = figure_axes(title=title, apctx=ctx)
    bars = ax.bar(np.arange(1, len(df.index) + 1), df["freq"])
    for i, mybar in enumerate(bars):
        ax.text(
            i + 1,
            mybar.get_height() + 0.3,
            f"{df['hit'].iloc[i]}",
            ha="center",
        )
    ax.set_ylabel("Frequency (%)")
    ax.set_xlabel(
        f"Day of {calendar.month_name[month]}, number of years "
        f"(out of {np.max(df['total'])}) meeting criteria labelled"
    )
    ax.grid(True)
    ax.set_xlim(0.5, 31.5)
    ax.set_ylim(0, df["freq"].max() + 5)

    return fig, df
