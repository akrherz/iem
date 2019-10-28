"""Office accumulated warnings"""
import datetime
import math
import calendar

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.nws import vtec
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem import reference
from pyiem.exceptions import NoDataFound

PDICT = {"yes": "Limit Plot to Year-to-Date", "no": "Plot Entire Year"}
PDICT2 = {
    "single": "Plot Single VTEC Phenomena + Significance",
    "svrtor": "Plot Severe Thunderstorm + Tornado Warnings",
}
PDICT3 = {"wfo": "Plot for Single/All WFO", "state": "Plot for a Single State"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 86400
    desc["data"] = True
    desc[
        "description"
    ] = """This plot displays an accumulated total of
    office issued watch, warning, advisories.  These totals are not official
    and based on IEM processing of NWS text warning data.  The totals are for
    individual warnings and not some combination of counties + warnings. The
    archive begin date varies depending on which phenomena you are interested
    in."""
    desc["arguments"] = [
        dict(
            type="select",
            name="opt",
            options=PDICT3,
            default="wfo",
            label="Plot for a WFO or a State?",
        ),
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO (when appropriate):",
            all=True,
        ),
        dict(
            type="state",
            default="IA",
            name="state",
            label="Select State (when appropriate):",
        ),
        dict(
            type="select",
            name="limit",
            default="no",
            label="End Date Limit to Plot:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="c",
            default="svrtor",
            label="Single or Combination of Products:",
            options=PDICT2,
        ),
        dict(
            type="phenomena",
            name="phenomena",
            default="TO",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="W",
            label="Select Watch/Warning Significance Level:",
        ),
        dict(
            type="year",
            name="syear",
            default=1986,
            min=1986,
            label="Inclusive Start Year (if data is available) for plot:",
        ),
        dict(
            type="year",
            name="eyear",
            default=datetime.date.today().year,
            min=1986,
            label="Inclusive End Year (if data is available) for plot:",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    limit = ctx["limit"]
    combo = ctx["c"]
    phenomena = ctx["phenomena"][:2]
    significance = ctx["significance"][:2]
    opt = ctx["opt"]
    state = ctx["state"][:2]
    syear = ctx["syear"]
    eyear = ctx["eyear"]

    ctx["_nt"].sts["_ALL"] = {"name": "All Offices"}
    if station not in ctx["_nt"].sts:
        raise NoDataFound("No Data Found.")

    lastdoy = 367
    if limit.lower() == "yes":
        lastdoy = int(datetime.datetime.today().strftime("%j")) + 1
    wfolimiter = " and wfo = '%s' " % (station,)
    if opt == "state":
        wfolimiter = " and substr(ugc, 1, 2) = '%s' " % (state,)
    if opt == "wfo" and station == "_ALL":
        wfolimiter = ""
    eventlimiter = ""
    if combo == "svrtor":
        eventlimiter = " or (phenomena = 'SV' and significance = 'W') "
        phenomena = "TO"
        significance = "W"

    cursor.execute(
        """
    WITH data as (
        SELECT extract(year from issue) as yr,
        issue, phenomena, significance, eventid, wfo from warnings WHERE
        ((phenomena = %s and significance = %s) """
        + eventlimiter
        + """)
        and extract(year from issue) >= %s and
        extract(year from issue) <= %s
        and extract(doy from issue) <= %s """
        + wfolimiter
        + """),
    agg1 as (
        SELECT yr, min(issue) as min_issue, eventid, wfo, phenomena,
        significance from data
        GROUP by yr, eventid, wfo, phenomena, significance),
    agg2 as (
        SELECT yr, extract(doy from min_issue) as doy, count(*)
        from agg1 GROUP by yr, doy)
    SELECT yr, doy, sum(count) OVER (PARTITION by yr ORDER by doy ASC)
    from agg2 ORDER by yr ASC, doy ASC
    """,
        (phenomena, significance, syear, eyear, lastdoy),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")

    data = {}
    for yr in range(syear, eyear + 1):
        data[yr] = {"doy": [0], "counts": [0]}
    rows = []
    for row in cursor:
        data[row[0]]["doy"].append(row[1])
        data[row[0]]["counts"].append(row[2])
        rows.append(dict(year=row[0], day_of_year=row[1], count=row[2]))
    # append on a lastdoy value so all the plots go to the end
    for yr in range(syear, eyear):
        if len(data[yr]["doy"]) == 1 or data[yr]["doy"][-1] >= lastdoy:
            continue
        data[yr]["doy"].append(lastdoy)
        data[yr]["counts"].append(data[yr]["counts"][-1])
    if data[eyear]["doy"]:
        data[eyear]["doy"].append(
            int(datetime.datetime.today().strftime("%j")) + 1
        )
        data[eyear]["counts"].append(data[eyear]["counts"][-1])
    df = pd.DataFrame(rows)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    ann = []
    for yr in range(syear, eyear + 1):
        if len(data[yr]["doy"]) < 2:
            continue
        lp = ax.plot(
            data[yr]["doy"],
            data[yr]["counts"],
            lw=2,
            label="%s (%s)" % (str(yr), data[yr]["counts"][-1]),
            drawstyle="steps-post",
        )
        ann.append(
            ax.text(
                data[yr]["doy"][-1] + 1,
                data[yr]["counts"][-1],
                "%s" % (yr,),
                color="w",
                va="center",
                fontsize=10,
                bbox=dict(
                    facecolor=lp[0].get_color(), edgecolor=lp[0].get_color()
                ),
            )
        )

    mask = np.zeros(fig.canvas.get_width_height(), bool)
    fig.canvas.draw()

    attempts = 10
    while ann and attempts > 0:
        attempts -= 1
        removals = []
        for a in ann:
            bbox = a.get_window_extent()
            x0 = int(bbox.x0)
            x1 = int(math.ceil(bbox.x1))
            y0 = int(bbox.y0)
            y1 = int(math.ceil(bbox.y1))

            s = np.s_[x0 : x1 + 1, y0 : y1 + 1]
            if np.any(mask[s]):
                a.set_position([a._x - int(lastdoy / 14), a._y])
            else:
                mask[s] = True
                removals.append(a)
        for rm in removals:
            ann.remove(rm)

    ax.legend(loc=2, ncol=2, fontsize=10)
    ax.set_xlim(1, 367)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_ylabel("Accumulated Count")
    ax.set_ylim(bottom=0)
    title = vtec.get_ps_string(phenomena, significance)
    if combo == "svrtor":
        title = "Severe Thunderstorm + Tornado Warning"
    ptitle = "%s" % (ctx["_nt"].sts[station]["name"],)
    if opt == "state":
        ptitle = ("NWS Issued for Counties/Parishes in %s") % (
            reference.state_names[state],
        )
    ax.set_title(("%s\n %s Count") % (ptitle, title))
    ax.set_xlim(0, lastdoy)
    if lastdoy < 367:
        ax.set_xlabel(
            ("thru approximately %s")
            % (datetime.date.today().strftime("%-d %B"),)
        )

    return fig, df


if __name__ == "__main__":
    plotter(dict())
