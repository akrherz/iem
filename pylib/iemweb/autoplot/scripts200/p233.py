"""
This calendar presents the number of Special Weather Statements
that contain polygons issued per day.
<a href="/plotting/auto/?q=143">Autoplot 143</a> presents this same data,
but as yearly and monthly totals.
"""

import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import calendar_plot
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {"yes": "Colorize Cells in Chart", "no": "Just plot values please"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    desc["arguments"] = [
        dict(
            type="date",
            name="sdate",
            default=jan1.strftime("%Y/%m/%d"),
            label="Start Date (inclusive):",
            min="1986/01/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="End Date (inclusive):",
            min="1986/01/01",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            all=True,
            default="DMX",
            label="Select WFO:",
        ),
        dict(
            type="select",
            name="heatmap",
            options=PDICT,
            default="yes",
            label="Colorize calendar cells based on values?",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    sts = ctx["sdate"]
    ets = ctx["edate"]
    if (ets - sts).days > 366:
        raise NoDataFound("Chart duration needs to be less than 1 year.")
    wfo = ctx["wfo"]
    params = {}
    params["tzname"] = ctx["_nt"].sts[wfo]["tzname"]
    params["sts"] = sts - datetime.timedelta(days=2)
    params["ets"] = ets + datetime.timedelta(days=2)

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
    title2 = f"NWS {ctx['_sname']}"
    if wfo == "_ALL":
        title2 = "All NWS Offices"
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
    select date(issue at time zone :tzname), count(*)
    from sps
    where not ST_IsEmpty(geom) {wfo_limiter} and
    issue >= :sts and issue < :ets GROUP by date
        """
            ),
            conn,
            params=params,
            index_col="date",
        )

    data = {}
    now = sts
    while now <= ets:
        data[now] = {"val": 0}
        now += datetime.timedelta(days=1)
    for date, row in df.iterrows():
        data[date] = {"val": row["count"]}
    fig = calendar_plot(
        sts,
        ets,
        data,
        apctx=ctx,
        heatmap=(ctx["heatmap"] == "yes"),
        title=f"Number of SPS Polygons for {title2} by Local Calendar Date",
        subtitle=f"Valid {sts:%d %b %Y} - {ets:%d %b %Y}",
    )
    return fig, df
