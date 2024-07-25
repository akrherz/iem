"""
This chart presents the daily frequency of the
given date having the prescribed number of previous days above or below
some provided treshold. <a href="/plotting/auto/?q=216">Autoplot 216</a>
provides actual streaks and yearly maximum values.

<p>The accumulated precipitation metric is for an inclusive number of trailing
days evaluated at that given day, so there is not double accounting for days
that participate in a trailing day period that ended in the future.  Rewording,
an example frequency of 25% of May 1 would indicate that on that date, it had
an inclusive trailing number of days accumulation above or below the choosen
threshold.

<p><strong>2 Oct 2023:</strong> The plotting logic was updated to plot
the frequency of a given day participating in a streak, rather than the
frequency of a streak ending on that day.  This should be a more useful
metric for the user.
"""

import calendar

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

from iemweb.autoplot import ARG_STATION

PDICT = {
    "above": "At or Above (AOA) Threshold",
    "below": "Below Threshold",
}
PDICT2 = {
    "precip": "Accumulated Precipitation",
    "low": "Low Temperature",
    "high": "High Temperature",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="var",
            default="high",
            options=PDICT2,
            label="Select which daily variable",
        ),
        dict(
            type="select",
            name="dir",
            default="above",
            options=PDICT,
            label="Select direction",
        ),
        dict(
            type="float",
            name="threshold",
            default="60",
            label="Threshold (F or inch):",
        ),
        dict(type="int", name="days", default="7", label="Number of Days:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = ctx["days"]
    threshold = ctx["threshold"]
    varname = ctx["var"]
    mydir = ctx["dir"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"select day, sday, {varname} from alldata where station = %s "
            "ORDER by day ASC",
            conn,
            params=(station,),
            index_col="day",
            parse_dates="day",
        )
    if df.empty:
        raise NoDataFound("No data found for station / threshold.")
    df["hit"] = False
    syear = df.index[0].year
    eyear = df.index[-1].year
    years = eyear - syear + 1
    if varname == "precip":
        df["trail"] = df[varname].rolling(window=f"{days}D").agg("sum")
    else:
        df["trail"] = (
            df[varname]
            .rolling(window=f"{days}D")
            .agg("min" if mydir == "above" else "max")
        )
    if mydir == "above":
        hits = df["trail"] >= threshold
    else:
        hits = df["trail"] < threshold
    if hits.sum() == 0:
        raise NoDataFound("No events found for threshold.")

    # Need to compute if a given date participated in a streak
    # shift hits back in time to match the days
    for day in range(days):
        df["hit"] = df["hit"] | hits.shift(0 - day)

    freq = df[["sday", "hit"]].groupby("sday").sum() / years * 100.0
    freq = freq.reindex(
        pd.date_range("2000-01-01", "2000-12-31").strftime("%m%d")
    ).fillna(0)

    label = "AOA" if mydir == "above" else "below"
    units = "inch" if varname == "precip" else r"$^\circ$F"
    title = (
        f"{ctx['_sname']} [{syear}-{eyear}] ::"
        f"Frequency of {days} Consec Days "
        f"with {varname.capitalize()} {label} {threshold} {units}"
    )
    fig, ax = figure_axes(apctx=ctx, title=title)
    ax.set_position([0.1, 0.1, 0.7, 0.8])
    ax.set_ylabel("Frequency of Streak Including Day of Year [%]")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.bar(range(366), freq["hit"], width=1)

    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    df = df[hits].sort_values("sday")
    ypos = 0.85
    xpos = 0.83
    fmt = "%.0f" if varname != "precip" else "%.2f"
    fig.text(xpos, ypos + 0.03, "End Date of Streak")
    fig.text(xpos - 0.015, ypos, "Earliest Dates   ", rotation=90, va="top")
    for day, row in df.head(10).iterrows():
        ypos -= 0.03
        txt = fmt % row["trail"]
        fig.text(xpos, ypos, f"{day.strftime('%-2d %b %Y')} {txt}")

    ypos -= 0.1
    fig.text(xpos - 0.015, ypos, "Latest Dates   ", rotation=90, va="top")
    for day, row in df.tail(10).iloc[::-1].iterrows():
        ypos -= 0.03
        txt = fmt % row["trail"]
        fig.text(xpos, ypos, f"{day.strftime('%-2d %b %Y')} {txt}")

    return fig, freq
