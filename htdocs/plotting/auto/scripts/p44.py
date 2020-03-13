"""Office accumulated warnings"""
import datetime
import math
import calendar

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.nws import vtec
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn, utc
from pyiem import reference
from pyiem.exceptions import NoDataFound

PDICT = {"yes": "Limit Plot to Year-to-Date", "no": "Plot Entire Year"}
PDICT2 = {
    "single": "Plot Single VTEC Phenomena + Significance",
    "svrtor": "Plot Severe Thunderstorm + Tornado Warnings",
}
PDICT3 = {"wfo": "Plot for Single/All WFO", "state": "Plot for a Single State"}
PDICT4 = {"line": "Accumulated line plot", "bar": "Single bar plot per year"}


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
    in.

    <p>Generally, the archive starts in Fall 2005 for most types.  Event
    counts do exist for Severe Thunderstorm, Tornado and Flash Flood warnings
    for dates back to 1986.  Data quality prior to 2001 is not the greatest
    though.
    """
    desc["arguments"] = [
        dict(
            type="select",
            name="plot",
            options=PDICT4,
            default="line",
            label="Which plot type to produce?",
        ),
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


def plot_common(ctx, ax):
    """Common plot stuff."""
    ax.set_ylabel("Accumulated Count")
    ax.grid(True)
    ax.set_title(ctx["title"])
    ax.set_xlabel(ctx["xlabel"])


def make_barplot(ctx, df):
    """Create a bar plot."""
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    df2 = (
        df.groupby("year").max().reindex(range(ctx["syear"], ctx["eyear"] + 1))
    )
    df2 = df2.fillna(0)
    ax.bar(df2.index.values, df2["count"])
    for year, row in df2.iterrows():
        ax.text(
            year,
            float(row["count"]) + 3,
            "%.0f" % (row["count"],),
            rotation=90 if len(df2.index) > 17 else 0,
            bbox=dict(color="white", boxstyle="square,pad=0.1"),
            ha="center",
        )
    ax.set_xlim(ctx["syear"] - 0.5, ctx["eyear"] + 0.5)
    ax.set_ylim(top=max(5, float(df2["count"].max()) * 1.2))
    plot_common(ctx, ax)
    return fig, df2


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
    if phenomena in ["SV", "TO", "FF"] and significance == "W":
        pass
    else:
        ctx["syear"] = max(ctx["syear"], 2005)
    opt = ctx["opt"]
    state = ctx["state"][:2]
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
        SELECT extract(year from issue)::int as yr,
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
        (phenomena, significance, ctx["syear"], eyear, lastdoy),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")

    data = {}
    for yr in range(ctx["syear"], eyear + 1):
        data[yr] = {"doy": [0], "counts": [0]}
    rows = []
    for row in cursor:
        data[row[0]]["doy"].append(row[1])
        data[row[0]]["counts"].append(row[2])
        rows.append(dict(year=row[0], day_of_year=row[1], count=row[2]))
    # append on a lastdoy value so all the plots go to the end
    for yr in range(ctx["syear"], eyear + 1):
        if data[yr]["doy"][-1] >= lastdoy:
            continue
        if yr == utc().year:
            # append today
            data[yr]["doy"].append(int(utc().strftime("%j")))
        else:
            data[yr]["doy"].append(lastdoy)
        data[yr]["counts"].append(data[yr]["counts"][-1])
    df = pd.DataFrame(rows)

    title = vtec.get_ps_string(phenomena, significance)
    if combo == "svrtor":
        title = "Severe Thunderstorm + Tornado Warning"
    ptitle = "NWS WFO: %s (%s)" % (ctx["_nt"].sts[station]["name"], station)
    if opt == "state":
        ptitle = ("NWS Issued for %s in %s") % (
            "Parishes" if state == "LA" else "Counties",
            reference.state_names[state],
        )
    ctx["title"] = "%s\n %s Count" % (ptitle, title)
    ctx["xlabel"] = "entire year plotted"
    if lastdoy < 367:
        ctx["xlabel"] = ("thru approximately %s") % (
            datetime.date.today().strftime("%-d %B"),
        )

    if ctx["plot"] == "bar":
        return make_barplot(ctx, df)
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    ann = []
    for yr in range(ctx["syear"], eyear + 1):
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
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])
    plot_common(ctx, ax)
    ax.set_ylim(bottom=0)
    ax.set_xlim(0, lastdoy)

    return fig, df


if __name__ == "__main__":
    plotter(
        dict(limit="yes", station="UNR", opt="wfo", c="svrtor", plot="bar")
    )
