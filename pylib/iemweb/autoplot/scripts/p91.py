"""
This plot produces statistics on min, max, and
average values of a variable over a window of days.  The labels get
a bit confusing, but we are looking for previous periods of time with
temperature
above or below a given threshold.  For precipitation, it is only a period
with each day above a given threshold and the average over that period.
<a href="/plotting/auto/?q=216">Autoplot 216</a>
provides actual streaks and yearly maximum values.
"""

import numpy as np
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.plot import figure_axes
from sqlalchemy.engine import Connection

from iemweb.autoplot import ARG_STATION

PDICT = {
    "high": "High Temperature",
    "low": "Low Temperature",
    "precip": "Precipitation",
    "snow": "Snowfall",
    "snowd": "Snow Depth",
}

UNITS = {
    "precip": "inch",
    "snow": "inch",
    "snowd": "inch",
    "high": "F",
    "low": "F",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="var",
            default="precip",
            label="Which Variable:",
            options=PDICT,
        ),
    ]
    return desc


@with_sqlalchemy_conn("coop")
def plotter(ctx: dict, conn: Connection | None = None):
    """Go"""
    station = ctx["station"]
    varname = ctx["var"]

    rows = []
    for dy in range(1, 32):
        res = conn.execute(
            sql_helper(
                """
            with data as (
            select day,
            avg({varname}) OVER
                (ORDER by day ASC rows between :d1 preceding and current row),
            min({varname}) OVER
                (ORDER by day ASC rows between :d1 preceding and current row),
            max({varname}) OVER
                (ORDER by day ASC rows between :d1 preceding and current row)
            from alldata where station = :station)
        SELECT max(avg), min(avg), max(min), min(min), max(max), min(max)
        from data
        """,
                varname=varname,
            ),
            {"d1": dy - 1, "station": station},
        )
        row = res.fetchone()
        rows.append(
            dict(
                days=dy,
                highest_avg=row[0],
                lowest_avg=row[1],
                highest_min=row[2],
                lowest_min=row[3],
                highest_max=row[4],
                lowest_max=row[5],
            )
        )
    df = pd.DataFrame(rows)

    title = (
        f"{ctx['_sname']} Statistics of {PDICT.get(varname)} "
        "over 1-31 Consecutive Days"
    )
    fig, ax = figure_axes(title=title, apctx=ctx)
    if varname == "precip":
        ax.plot(
            np.arange(1, 32),
            df["highest_avg"],
            color="b",
            label="Highest Average",
            lw=2,
        )
        ax.plot(
            np.arange(1, 32),
            df["highest_min"],
            color="g",
            label="Consec Days Over",
            lw=2,
        )
        ax.plot(
            np.arange(1, 32),
            df["lowest_min"],
            color="r",
            label="Consec Days Under",
            lw=2,
        )
    else:
        ax.plot(
            np.arange(1, 32), df["highest_avg"], label="Highest Average", lw=2
        )
        ax.plot(
            np.arange(1, 32), df["lowest_avg"], label="Lowest Average", lw=2
        )
        ax.plot(
            np.arange(1, 32), df["highest_min"], label="Highest Above", lw=2
        )
        ax.plot(np.arange(1, 32), df["lowest_max"], label="Lowest Below", lw=2)
    ax.set_ylabel(f"{PDICT.get(varname)} ({UNITS.get(varname)})")
    ax.set_xlabel("Consecutive Days")
    ax.grid(True)
    ax.set_xlim(0.5, 31.5)

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
    )

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        fancybox=True,
        shadow=True,
        ncol=3,
        scatterpoints=1,
        fontsize=12,
    )

    return fig, df
