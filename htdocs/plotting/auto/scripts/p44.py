"""Office accumulated warnings"""
import datetime
import math
import calendar

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.nws import vtec
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem import reference
from pyiem.exceptions import NoDataFound

PDICT = {"yes": "Limit Plot to Year-to-Date", "no": "Plot Entire Year"}
PDICT2 = {
    "single": "Plot Single VTEC Phenomena + Significance",
    "svrtor": "Plot Severe Thunderstorm + Tornado Warnings",
    "all": "Plot All VTEC Events",
}
PDICT3 = {"wfo": "Plot for Single/All WFO", "state": "Plot for a Single State"}
PDICT4 = {"line": "Accumulated line plot", "bar": "Single bar plot per year"}
PDICT5 = {"jan1": "January 1", "jul1": "July 1"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
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
    though.</p>

    <p>If you want to use the "cold season" as the basis of a year, pick the
    "July 1" option below. The "year" label is then associated with the fall
    portion of the cold season (1 Jul 2021 - 30 Jun 2022 is 2021).
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
        dict(
            type="select",
            name="s",
            default="jan1",
            options=PDICT5,
            label="Start date of the 'year' plotted",
        ),
    ]
    return desc


def plot_common(ctx, ax):
    """Common plot stuff."""
    ax.set_ylabel("Accumulated Count")
    ax.grid(True)
    ax.set_xlabel(ctx["xlabel"])


def make_barplot(ctx, df):
    """Create a bar plot."""
    fig = figure(title=ctx["title"])
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    df2 = (
        df.groupby("year").max().reindex(range(ctx["syear"], ctx["eyear"] + 1))
    )
    df2 = df2.fillna(0)
    ax.bar(df2.index.values, df2["count"])
    for year, row in df2.iterrows():
        ax.text(
            year,
            float(row["count"]) + 3,
            f"{row['count']:.0f}",
            rotation=90 if len(df2.index) > 17 else 0,
            bbox=dict(color="white", boxstyle="square,pad=0.1"),
            ha="center",
        )
    ax.set_xlim(ctx["syear"] - 0.5, ctx["eyear"] + 0.5)
    ax.set_ylim(top=max(5, float(df2["count"].max()) * 1.2))
    plot_common(ctx, ax)
    return fig, df2


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    limit = ctx["limit"]
    combo = ctx["c"]
    phenomena = ctx["phenomena"][:2]
    significance = ctx["significance"][:1]
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
        if ctx["s"] == "jul1":
            raise ValueError("Sorry, combination of Jul 1 + limit supported")
        lastdoy = int(datetime.datetime.today().strftime("%j")) + 1
    wfolimiter = f" and wfo = '{station}' "
    if opt == "state":
        wfolimiter = f" and substr(ugc, 1, 2) = '{state}' "
    if opt == "wfo" and station == "_ALL":
        wfolimiter = ""
    eventlimiter = ""
    if combo == "svrtor":
        eventlimiter = " or (phenomena = 'SV' and significance = 'W') "
        phenomena = "TO"
        significance = "W"
    args = [ctx["syear"], eyear, lastdoy]
    if combo == "all":
        pslimiter = ""
    else:
        pslimiter = "(phenomena = %s and significance = %s)"
        args.insert(0, significance)
        args.insert(0, phenomena)

    limiter = ""
    if pslimiter != "" or eventlimiter != "":
        limiter = f" ({pslimiter} {eventlimiter}) and "

    df = read_sql(
        f"""
    WITH data as (
        SELECT extract(year from issue)::int as year,
        issue, phenomena, significance, eventid, wfo from warnings WHERE
        {limiter} extract(year from issue) >= %s and
        extract(year from issue) <= %s
        and extract(doy from issue) <= %s {wfolimiter}),
    agg1 as (
        SELECT year, min(issue) as min_issue, eventid, wfo, phenomena,
        significance from data
        GROUP by year, eventid, wfo, phenomena, significance)

    SELECT date(min_issue) as date, count(*)
    from agg1 GROUP by date ORDER by date ASC
    """,
        get_dbconn("postgis"),
        params=args,
        index_col="date",
        parse_dates="date",
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df = df.reindex(
        pd.date_range(df.index.values[0], df.index.values[-1])
    ).fillna(0)
    df["year"] = df.index.year
    df["month"] = df.index.month
    if ctx["s"] == "jul1":
        # Munge the year
        df.at[df["month"] < 7, "year"] = df["year"] - 1
    # Compute cumsum
    df["cumsum"] = df[["year", "count"]].groupby("year").cumsum()

    title = vtec.get_ps_string(phenomena, significance)
    if combo == "svrtor":
        title = "Severe Thunderstorm + Tornado Warning"
    elif combo == "all":
        title = "All VTEC Events"
    ptitle = f"NWS WFO: {ctx['_nt'].sts[station]['name']} ({station})"
    if opt == "state":
        ptitle = ("NWS Issued for %s in %s") % (
            "Parishes" if state == "LA" else "Counties",
            reference.state_names[state],
        )
    ctx["title"] = f"{ptitle}\n {title} Count"
    ctx["xlabel"] = "all days plotted"
    if lastdoy < 367:
        ctx["xlabel"] = f"thru approximately {datetime.date.today():%-d %B}"
    if ctx["s"] == "jul1":
        ctx["xlabel"] += ", year denotes start date of 1 July"

    if ctx["plot"] == "bar":
        return make_barplot(ctx, df)
    fig = figure(title=ctx["title"])
    ax = fig.add_axes([0.05, 0.1, 0.65, 0.8])
    ann = []
    for yr in range(ctx["syear"], eyear + 1):
        df2 = df[df["year"] == yr]
        if len(df2.index) < 2:
            continue
        basedate = datetime.date(yr, 7 if ctx["s"] == "jul1" else 1, 1)
        xr = [x.days for x in (df2.index.date - basedate)]
        maxval = df2["cumsum"].max()
        lp = ax.plot(
            xr,
            df2["cumsum"],
            lw=2,
            label=f"{yr} ({maxval:.0f})",
            drawstyle="steps-post",
        )
        lrow = df2[df2["cumsum"] == maxval].index.date[0]
        ann.append(
            ax.text(
                (lrow - basedate).days + 1,
                maxval,
                f"{yr}",
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

    ax.legend(loc=(1.07, 0), ncol=2, fontsize=10)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    if ctx["s"] == "jan1":
        ax.set_xticklabels(calendar.month_abbr[1:])
    else:
        labels = calendar.month_abbr[7:]
        labels.extend(calendar.month_abbr[1:7])
        ax.set_xticklabels(labels)
    plot_common(ctx, ax)
    ax.set_ylim(bottom=0)
    ax.set_xlim(0, lastdoy)

    return fig, df


if __name__ == "__main__":
    plotter(
        {
            "limit": "yes",
            "station": "UNR",
            "opt": "wfo",
            "c": "single",
            "s": "jul1",
        }
    )
