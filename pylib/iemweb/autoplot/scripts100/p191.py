"""
This application presents a calendar of daily
counts of the number of watch, warning, advisories issued by day.  This
accounting is based on the initial issuance date of a given VTEC phenomena
and significance by event identifier.  So a single Winter Storm Watch
for 40 zones, would only count as 1 event for this chart.  Dates are
computed in the local time zone of the issuance forecast office in the
case of a single office and in Central Time for the case of all offices of
plotting a given state.

<p>You can also generate this plot considering "ALL" NWS Offices, when
doing so the time zone used to compute the calendar dates is US Central.
"""

from datetime import date, timedelta

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import calendar_plot
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import ARG_FEMA, fema_region2states

PDICT = {"yes": "Colorize Cells in Chart", "no": "Just plot values please"}
PDICT2 = {
    "wfo": "Summarize by Selected WFO",
    "state": "Summarize by Selected State",
    "ugc": "Summaryize by NWS County/Forecast Zone",
    "fema": "Summarize by FEMA Region",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = date.today()
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
            type="select",
            name="w",
            options=PDICT2,
            default="wfo",
            label="How to summarize data:",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            all=True,
            default="DMX",
            label="Select WFO (when appropriate):",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State (when appropriate):",
        ),
        ARG_FEMA,
        dict(
            type="ugc",
            name="ugc",
            default="IAC169",
            label="Select UGC Zone/County:",
        ),
        dict(
            type="select",
            name="heatmap",
            options=PDICT,
            default="yes",
            label="Colorize calendar cells based on values?",
        ),
        dict(
            type="vtec_ps",
            name="v1",
            default="SV.W",
            label="VTEC Phenomena and Significance 1",
        ),
        dict(
            type="vtec_ps",
            name="v2",
            default="SV.W",
            optional=True,
            label="VTEC Phenomena and Significance 2",
        ),
        dict(
            type="vtec_ps",
            name="v3",
            default="SV.W",
            optional=True,
            label="VTEC Phenomena and Significance 3",
        ),
        dict(
            type="vtec_ps",
            name="v4",
            default="SV.W",
            optional=True,
            label="VTEC Phenomena and Significance 4",
        ),
    ]
    return desc


def get_ugc_name(ugc):
    """Return the WFO and county name."""
    cursor = get_dbconn("postgis").cursor()
    cursor.execute(
        "SELECT name, wfo from ugcs where ugc = %s and end_ts is null", (ugc,)
    )
    return cursor.fetchone()


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
    p1 = ctx["phenomenav1"]
    p2 = ctx["phenomenav2"]
    p3 = ctx["phenomenav3"]
    p4 = ctx["phenomenav4"]
    phenomena = [p[:2] for p in [p1, p2, p3, p4] if p is not None]
    s1 = ctx["significancev1"]
    s2 = ctx["significancev2"]
    s3 = ctx["significancev3"]
    s4 = ctx["significancev4"]
    significance = [s[0] for s in [s1, s2, s3, s4] if s is not None]

    pstr = []
    title = []
    params = {}
    params["tzname"] = ctx["_nt"].sts[wfo]["tzname"]
    params["sts"] = sts - timedelta(days=2)
    params["ets"] = ets + timedelta(days=2)
    for i, (p, s) in enumerate(zip(phenomena, significance)):
        pstr.append(f"(phenomena = :ph{i} and significance = :sig{i})")
        params[f"ph{i}"] = p
        params[f"sig{i}"] = s
        if i == 2:
            title[-1] += "\n"
        title.append(f"{vtec.get_ps_string(p, s)} {p}.{s}")
    title = ", ".join(title)
    pstr = " or ".join(pstr)
    pstr = f"({pstr})"

    if ctx["w"] == "wfo":
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
    elif ctx["w"] == "ugc":
        wfo_limiter = " and ugc = :ugc "
        params["ugc"] = ctx["ugc"]
        name, wfo = get_ugc_name(ctx["ugc"])
        title2 = f"[{ctx['ugc']}] {name}"
    elif ctx["w"] == "fema":
        wfo_limiter = " and substr(ugc, 1, 2) = ANY(:states) "
        params["states"] = fema_region2states(ctx["fema"])
        title2 = f"FEMA Region {ctx['fema']}"
    else:
        wfo_limiter = " and substr(ugc, 1, 2) = :state "
        params["state"] = ctx["state"]
        title2 = state_names[ctx["state"]]
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
    with events as (
    select wfo, min(issue at time zone :tzname) as localissue, vtec_year,
    phenomena, significance, eventid from warnings
    where {pstr} {wfo_limiter} and
    issue >= :sts and issue < :ets
    GROUP by wfo, vtec_year, phenomena, significance, eventid
    )

    SELECT date(localissue), count(*) from events GROUP by date(localissue)
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
        now += timedelta(days=1)
    for dt, row in df.iterrows():
        data[dt] = {"val": row["count"]}
    aa = "VTEC Events"
    if len(significance) == 1:
        aa = f"{vtec.get_ps_string(phenomena[0], significance[0])} Count"
    fig = calendar_plot(
        sts,
        ets,
        data,
        apctx=ctx,
        heatmap=(ctx["heatmap"] == "yes"),
        title=f"{aa} for {title2} by Local Calendar Date",
        subtitle=f"Valid {sts:%d %b %Y} - {ets:%d %b %Y} for {title}",
    )
    return fig, df
