"""
This calendar presents the number of Special Weather Statements
that contain polygons issued per day.
<a href="/plotting/auto/?q=143">Autoplot 143</a> presents this same data,
but as yearly and monthly totals.
"""

from datetime import date, timedelta
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import calendar_plot

from iemweb.autoplot.description import (
    DateArg,
    NetworkSelectArg,
    PlotDescription,
    SelectArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {"yes": "Colorize Cells in Chart", "no": "Just plot values please"}


class Params(AutoplotParams):
    """Request parameters."""

    sdate: Annotated[
        date,
        DateArg(
            label="Start Date (inclusive):",
            min="1986/01/01",
            default=lambda: (
                date.today().replace(month=1, day=1).strftime("%Y/%m/%d")
            ),
        ),
    ]
    edate: Annotated[
        date,
        DateArg(
            label="End Date (inclusive):",
            min="1986/01/01",
            default=lambda: date.today().strftime("%Y/%m/%d"),
        ),
    ]
    wfo: Annotated[
        str, NetworkSelectArg(network="WFO", all=True, label="Select WFO:")
    ] = "DMX"
    heatmap: Annotated[
        str,
        SelectArg(
            options=PDICT, label="Colorize calendar cells based on values?"
        ),
    ] = "yes"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    sts = ctx.sdate
    ets = ctx.edate
    if (ets - sts).days > 366:
        raise NoDataFound("Chart duration needs to be less than 1 year.")
    wfo = ctx.wfo
    params = {}
    params["tzname"] = ctx["_nt"].sts[wfo]["tzname"]
    params["sts"] = sts - timedelta(days=2)
    params["ets"] = ets + timedelta(days=2)

    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    if wfo not in ctx["_nt"].sts:
        raise NoDataFound("No Data Found.")
    wfo_limiter = " and wfo = :wfo "
    params["wfo"] = wfo if len(wfo) == 3 else wfo[1:]
    if wfo == "_ALL":
        wfo_limiter = ""
    title2 = f"NWS {ctx.sname}"
    if wfo == "_ALL":
        title2 = "All NWS Offices"
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper(
                """
    select date(issue at time zone :tzname), count(*)
    from sps
    where not ST_IsEmpty(geom) {wfo_limiter} and
    issue >= :sts and issue < :ets GROUP by date
        """,
                wfo_limiter=wfo_limiter,
            ),
            conn,
            params=params,
            index_col="date",
        )

    data = {}
    now = sts
    while now <= ets:
        data[now] = {"val": 0}
        now += timedelta(days=1)
    for dt, row in df.iterrows():
        data[dt] = {"val": row["count"]}
    fig = calendar_plot(
        sts,
        ets,
        data,
        apctx=ctx,
        heatmap=(ctx.heatmap == "yes"),
        title=f"Number of SPS Polygons for {title2} by Local Calendar Date",
        subtitle=f"Valid {sts:%d %b %Y} - {ets:%d %b %Y}",
    )
    return fig, df
