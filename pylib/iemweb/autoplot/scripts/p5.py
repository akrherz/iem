"""
This plot displays the dates with the monthly
record of your choice displayed. In the case of ties, only the most
recent occurence is shown.
"""

import calendar

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION

PDICT = {
    "min_range": "Minimum Daily High to Low Temperature Range",
    "max_range": "Maximum Daily High to Low Temperature Range",
    "max_high": "Maximum Daily High Temperature",
    "max_low": "Maximum Daily Low Temperature",
    "min_high": "Minimum Daily High Temperature",
    "min_low": "Minimum Daily Low Temperature",
    "max_precip": "Maximum Daily Precipitation",
    "max_snow": "Maximum Daily Snowfall",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"data": True, "description": __doc__}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="var",
            default="min_range",
            label="Select Variable",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    varname = ctx["var"]

    tokens = varname.split("_")
    orderer = "(high - low)"
    if tokens[1] != "range":
        orderer = tokens[1]

    if tokens[0] == "min":
        orderer += " ASC"
    else:
        orderer += " DESC"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(f"""
        WITH ranks as (
            SELECT month, day, high, low, precip, snow,
            rank() OVER (
                PARTITION by month ORDER by {orderer} NULLS LAST)
            from alldata WHERE station = :station)

        select month, day, to_char(day, 'Mon dd, YYYY') as dd, high, low,
        precip, snow, (high - low) as range from ranks
        WHERE rank = 1 ORDER by month ASC, day DESC
        """),
            conn,
            params={"station": station},
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    labels = []
    ranges = []
    months = []
    for _, row in df.iterrows():
        if row["month"] in months:
            if labels[-1].endswith("*"):
                continue
            labels[-1] += " *"
            continue
        months.append(row["month"])
        if tokens[1] == "range":
            labels.append(
                f"{row[tokens[1]]} ({row['high']}/{row['low']}) - {row['dd']}"
            )
        else:
            labels.append(f"{row[tokens[1]]} - {row['dd']}")
        ranges.append(row[tokens[1]])

    syear = "n/a"
    if ctx["_nt"].sts[station]["archive_begin"] is not None:
        syear = ctx["_nt"].sts[station]["archive_begin"].year
    eyear = utc().year
    title = f"{ctx['_sname']} ({syear}-{eyear})\n" f"{PDICT[varname]} by Month"

    fig = figure(title=title, apctx=ctx)

    # Subplot showing the data
    ax = fig.add_axes((0.12, 0.1, 0.5, 0.8))
    ax.barh(np.arange(1, 13), ranges, align="center")
    ax.set_yticks(range(13))
    ax.set_yticklabels(calendar.month_name)
    ax.set_ylim(0, 13)
    ax.set_xlabel(
        "Date most recently set/tied shown, * indicates ties are present"
    )
    ax.grid(True)
    for i, label in enumerate(labels, start=1):
        ax.annotate(
            label,
            xy=(1.01, i),
            xycoords=("axes fraction", "data"),
            va="center",
        )

    # Create another axis for a cartoon for each month entry to denote the
    # day of the month the record occurred with a carrot
    ax = fig.add_axes((0.8, 0.1, 0.17, 0.8), frameon=False)
    ax.set_xticks([])
    ax.set_yticks([])
    for i in range(1, 13):
        for d in [8, 15, 22, 29]:
            ax.plot([d, d], [i - 0.1, i + 0.1], lw=2, color="#EEE", zorder=2)
            if i == 1:
                ax.text(d, 1 - 0.1, f"{d}", color="tan", ha="center", va="top")
        ax.plot([1, 31], [i, i], lw=2, color="tan", zorder=3)
        for _, row in df[df["month"] == i].iterrows():
            ax.scatter(
                row["day"].day,
                i + 0.06,
                marker="v",
                color="red",
                s=20,
                zorder=4,
            )
    ax.text(31, 12.5, "Day of Month\nRecord(s) Exist", ha="right", va="bottom")
    ax.set_ylim(0, 13)
    ax.set_xlim(-1, 33)  # give some space

    return fig, df
