"""
This plot attempts to show the impact of cloudiness
on temperatures.  The plot shows a simple difference between the average
temperature during cloudy/mostly cloudy conditions and the average
temperature by hour and by week of the year.  The input data for this
chart is limited to post 1973 as cloud cover data since then is more
reliable/comparable.
"""

from datetime import date

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes, get_cmap

PDICT = {
    "clear": "clear",
    "cloudy": "mostly cloudy",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            name="which",
            default="cloudy",
            options=PDICT,
            label="Compute differences based on:",
        ),
        dict(
            type="cmap", name="cmap", default="RdYlGn_r", label="Color Ramp:"
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["zstation"]
    which = ctx["which"]

    data = np.zeros((24, 52), "f")

    sql = "in ('BKN','OVC')" if which == "cloudy" else "= 'CLR'"
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        WITH data as (
        SELECT valid at time zone :tzname + '10 minutes'::interval as v,
        tmpf, skyc1, skyc2, skyc3, skyc4 from alldata WHERE station = :station
        and valid > '1973-01-01'
        and tmpf is not null and tmpf > -99 and tmpf < 150),


        climo as (
        select extract(week from v) as w,
        extract(hour from v) as hr,
        avg(tmpf) from data GROUP by w, hr),

        cloudy as (
        select extract(week from v) as w,
        extract(hour from v) as hr,
        avg(tmpf) from data WHERE skyc1 {op} or skyc2 {op} or
        skyc3 {op} or skyc4 {op} GROUP by w, hr)

        SELECT l.w as week, l.hr as hour, l.avg - c.avg as difference
        from cloudy l JOIN climo c on
        (l.w = c.w and l.hr = c.hr)
        """,
                op=sql,
            ),
            conn,
            params={
                "tzname": ctx["_nt"].sts[station]["tzname"],
                "station": station,
            },
        )

    for _, row in df.iterrows():
        if row["week"] > 52:
            continue
        data[int(row["hour"]), int(row["week"]) - 1] = row["difference"]
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    title = (
        f"{ctx['_sname']} "
        f"({max([ab.year, 1973])}-{date.today().year})\n"
        f"Hourly Temp Departure (skies were {PDICT[ctx['which']]} vs all)"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    maxv = np.ceil(max([np.max(data), 0 - np.min(data)])) + 0.2
    cs = ax.imshow(
        data,
        aspect="auto",
        interpolation="nearest",
        vmin=(0 - maxv),
        vmax=maxv,
        cmap=get_cmap(ctx["cmap"]),
    )
    a = fig.colorbar(cs)
    a.ax.set_ylabel("Temperature Departure °F")
    ax.grid(True)
    ax.set_ylim(-0.5, 23.5)
    ax.set_ylabel(f"Local Hour of Day, {ctx['_nt'].sts[station]['tzname']}")
    ax.set_yticks((0, 4, 8, 12, 16, 20))
    ax.set_xticks(range(0, 55, 7))
    ax.set_xticklabels(
        (
            "Jan 1",
            "Feb 19",
            "Apr 8",
            "May 27",
            "Jul 15",
            "Sep 2",
            "Oct 21",
            "Dec 9",
        )
    )
    ax.set_yticklabels(("Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"))

    return fig, df
