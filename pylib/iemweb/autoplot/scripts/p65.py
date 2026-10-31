"""
This plot displays the frequency of a given day
in the month having the coldest high or low temperature of that month for
a year.
"""

import calendar
from datetime import date, datetime, timedelta
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import MonthArg, PlotDescription, SelectArg
from iemweb.autoplot.params import AutoplotParams

PDICT = {"cold": "Coldest Temperature", "hot": "Hottest Temperature"}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    month: Annotated[
        int,
        MonthArg(label="Select Month:", default=lambda: date.today().month),
    ]
    dir: Annotated[
        str, SelectArg(label="Select variable to plot:", options=PDICT)
    ] = "cold"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    month = ctx.month
    mydir = ctx.dir
    ts = datetime(2000, month, 1)
    ets = ts + timedelta(days=35)
    ets = ets.replace(day=1)
    days = int((ets - ts).days)

    s = "ASC" if mydir == "cold" else "DESC"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            with ranks as (
                select day, high, low,
        rank() OVER (PARTITION by year ORDER by high {s}) as high_rank,
        rank() OVER (PARTITION by year ORDER by low {s}) as low_rank
                from alldata where station = :station and month = :month),
            highs as (
                SELECT extract(day from day) as dom, count(*) from ranks
                where high_rank = 1 GROUP by dom),
            lows as (
                SELECT extract(day from day) as dom, count(*) from ranks
                where low_rank = 1 GROUP by dom)

            select coalesce(h.dom, l.dom) as dom, h.count as high_count,
            l.count as low_count from
            highs h FULL OUTER JOIN lows l on (h.dom = l.dom) ORDER by h.dom
        """,
                s=s,
            ),
            conn,
            params={"station": station, "month": month},
        )

    fig = figure(apctx=ctx)
    ax = fig.subplots(2, 1, sharex=True)
    lbl = "Coldest" if mydir == "cold" else "Hottest"
    # match suptitle for plot2
    ax[0].set_title(
        (
            f"{ctx.sname}\n"
            f"Frequency of Day in {calendar.month_name[month]}\n"
            f"Having {lbl} High Temperature of {calendar.month_name[month]}"
        ),
        fontsize=10,
    )
    ax[0].set_ylabel("Years (ties split)")

    ax[0].grid(True)
    ax[0].bar(df["dom"], df["high_count"], align="center")

    ax[1].set_title(
        f"Having {lbl} Low Temperature of {calendar.month_name[month]}",
        fontsize=10,
    )
    ax[1].set_ylabel("Years (ties split)")
    ax[1].grid(True)
    ax[1].set_xlabel(f"Day of {calendar.month_name[month]}")
    ax[1].bar(df["dom"], df["low_count"], align="center")
    ax[1].set_xlim(0.5, days + 0.5)

    return fig, df
