"""
This plot displays the frequency of a given day
in the month having the coldest high or low temperature of that month for
a year.
"""

import calendar
import datetime

import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

from iemweb.autoplot import ARG_STATION

PDICT = {"cold": "Coldest Temperature", "hot": "Hottest Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="month",
            name="month",
            default=today.month,
            label="Select Month:",
        ),
        dict(
            type="select",
            name="dir",
            default="cold",
            label="Select variable to plot:",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]
    mydir = ctx["dir"]
    ts = datetime.datetime(2000, month, 1)
    ets = ts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)
    days = int((ets - ts).days)

    s = "ASC" if mydir == "cold" else "DESC"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
            with ranks as (
                select day, high, low,
        rank() OVER (PARTITION by year ORDER by high {s}) as high_rank,
        rank() OVER (PARTITION by year ORDER by low {s}) as low_rank
                from alldata where station = %s and month = %s),
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
            conn,
            params=(station, month),
        )

    fig = figure(apctx=ctx)
    ax = fig.subplots(2, 1, sharex=True)
    lbl = "Coldest" if mydir == "cold" else "Hottest"
    # match suptitle for plot2
    ax[0].set_title(
        (
            f"{ctx['_sname']}\n"
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
