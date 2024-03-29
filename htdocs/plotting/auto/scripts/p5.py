"""
This plot displays the dates with the monthly
record of your choice displayed. In the case of ties, only the most
recent occurence is shown.
"""

import calendar
import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

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
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
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
            f"""
        WITH ranks as (
            SELECT month, day, high, low, precip, snow,
            rank() OVER (
                PARTITION by month ORDER by {orderer} NULLS LAST)
            from alldata WHERE station = %s)

        select month, to_char(day, 'Mon dd, YYYY') as dd, high, low, precip,
        snow, (high - low) as range from ranks
        WHERE rank = 1 ORDER by month ASC, day DESC
        """,
            conn,
            params=(station,),
            index_col="month",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    labels = []
    ranges = []
    months = []
    for i, row in df.iterrows():
        if i in months:
            if labels[-1].endswith("*"):
                continue
            labels[-1] += " *"
            continue
        months.append(i)
        if tokens[1] == "range":
            labels.append(
                f"{row[tokens[1]]} ({row['high']}/{row['low']}) - {row['dd']}"
            )
        else:
            labels.append(f"{row[tokens[1]]} - {row['dd']}")
        ranges.append(row[tokens[1]])

    syear = ctx["_nt"].sts[station]["archive_begin"].year
    eyear = datetime.date.today().year
    title = f"{ctx['_sname']} ({syear}-{eyear})\n" f"{PDICT[varname]} by Month"

    (fig, ax) = figure_axes(title=title, apctx=ctx)

    ax.barh(np.arange(1, 13), ranges, align="center")
    ax.set_yticks(range(13))
    ax.set_yticklabels(calendar.month_name)
    ax.set_ylim(0, 13)
    ax.set_xlabel(
        "Date most recently set/tied shown, * indicates ties are present"
    )

    box = ax.get_position()
    ax.set_position([0.15, box.y0, box.width * 0.7, box.height])
    ax.grid(True)

    ax2 = ax.twinx()
    ax2.set_yticks(range(1, 13))
    ax2.set_yticklabels(labels)
    ax2.set_position([0.15, box.y0, box.width * 0.7, box.height])
    ax2.set_ylim(0, 13)

    return fig, df


if __name__ == "__main__":
    plotter({})
