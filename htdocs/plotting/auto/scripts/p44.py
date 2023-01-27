"""Office accumulated warnings"""
import datetime
import math
import calendar

import numpy as np
import pandas as pd
from pyiem.nws import vtec
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem import reference
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

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
    portion of the cold season (1 Jul 2021 - 30 Jun 2022 is 2021).</p>

    <p><strong>Updated 26 Jan 2023</strong> When selecting to limit to a year
    to date period, a more exact algorithm is now used to accumulate warnings
    through the end of the current date in central timezone.</p>
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
    fig = figure(title=ctx["title"], apctx=ctx)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    df2 = (
        df.groupby("year").sum().reindex(range(ctx["syear"], ctx["eyear"] + 1))
    )
    df2 = df2.fillna(0)
    ax.bar(df2.index.values, df2["count"])
    top = max(5, float(df2["count"].max()) * 1.2)
    for year, row in df2.iterrows():
        ax.text(
            year,
            float(row["count"]) + (top * 0.025),
            f"{row['count']:.0f}",
            rotation=90 if len(df2.index) > 17 else 0,
            bbox=dict(color="white", boxstyle="square,pad=0"),
            ha="center",
        )
    ax.set_xlim(ctx["syear"] - 0.5, ctx["eyear"] + 0.5)
    ax.set_ylim(top=top)
    plot_common(ctx, ax)
    return fig, df2


def munge_df(ctx, df):
    """Rectify an x-axis."""
    # Create sday
    df["sday"] = df.index.strftime("%m%d")
    df["year"] = df.index.year
    df["month"] = df.index.month

    # Rectify the year, if we are starting on jul1
    if ctx["s"] == "jul1":
        df.loc[df["month"] < 7, "year"] = df["year"] - 1

    # Create a baseline for a common xaxis
    month = 7 if ctx["s"] == "jul1" else 1
    baseline = pd.to_datetime({"year": df["year"], "month": month, "day": 1})
    df["xaxis"] = (df.index - baseline).astype(int) // 86400 // 1e9

    # If not limiting, we are done
    if ctx["limit"] == "no":
        return df

    today_sday = datetime.date.today().strftime("%m%d")
    # If year starts on jan1, easy
    if ctx["s"] == "jan1":
        return df[df["sday"] <= today_sday]

    if today_sday >= "0701":
        return df[(df["sday"] >= "0701") & (df["sday"] <= today_sday)]

    return df[(df["sday"] <= today_sday) | (df["sday"] >= "0701")]


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
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

    params = {"syear": ctx["syear"], "eyear": eyear}
    wfolimiter = " and wfo = :wfo "
    params["wfo"] = station
    if opt == "state":
        wfolimiter = " and substr(ugc, 1, 2) = :state "
        params["state"] = state
    if opt == "wfo" and station == "_ALL":
        wfolimiter = ""
    eventlimiter = ""
    if combo == "svrtor":
        eventlimiter = " or (phenomena = 'SV' and significance = 'W') "
        phenomena = "TO"
        significance = "W"
    if combo == "all":
        pslimiter = ""
    else:
        pslimiter = "(phenomena = :ph and significance = :sig)"
        params["ph"] = phenomena
        params["sig"] = significance

    limiter = ""
    if pslimiter != "" or eventlimiter != "":
        limiter = f" ({pslimiter} {eventlimiter}) and "
    # Load up all data by default and then filter it later.
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
        WITH data as (
            SELECT extract(year from issue)::int as year,
            issue, phenomena, significance, eventid, wfo from warnings WHERE
            {limiter} extract(year from issue) >= :syear and
            extract(year from issue) <= :eyear {wfolimiter}),
        agg1 as (
            SELECT year, min(issue) as min_issue, eventid, wfo, phenomena,
            significance from data
            GROUP by year, eventid, wfo, phenomena, significance)

        SELECT date(min_issue) as date, count(*)
        from agg1 GROUP by date ORDER by date ASC
        """
            ),
            conn,
            params=params,
            index_col="date",
            parse_dates="date",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    # pylint: disable=no-member
    df = df.reindex(
        pd.date_range(df.index.values[0], datetime.date.today())
    ).fillna(0)
    df = munge_df(ctx, df)
    # Compute cumsum
    df["cumsum"] = df[["year", "count"]].groupby("year").cumsum()

    title = vtec.get_ps_string(phenomena, significance)
    if combo == "svrtor":
        title = "Severe Thunderstorm + Tornado Warning"
    elif combo == "all":
        title = "All VTEC Events"
    ptitle = f"NWS WFO: {ctx['_nt'].sts[station]['name']} ({station})"
    if station == "_ALL":
        ptitle = "All NWS Offices"
    if opt == "state":
        _p = "Parishes" if state == "LA" else "Counties"
        ptitle = f"NWS Issued for {_p} in {reference.state_names[state]}"
    ctx["xlabel"] = "all days plotted"
    if ctx["limit"] == "yes":
        mm = "January 1" if ctx["s"] == "jan1" else "July 1"
        ctx["xlabel"] = f"{mm} through {datetime.date.today():%B %-d}"
        ptitle = f"{ptitle} [{ctx['xlabel']}]"
        if ctx["s"] == "jul1":
            ctx["xlabel"] += " (Year for July 1 shown)"
    ctx["title"] = f"{ptitle}\n{title} Count"

    if ctx["plot"] == "bar":
        return make_barplot(ctx, df)
    fig = figure(title=ctx["title"], apctx=ctx)
    ax = fig.add_axes([0.05, 0.1, 0.65, 0.8])
    ann = []
    for yr in range(ctx["syear"], eyear + 1):
        df2 = df[df["year"] == yr]
        if len(df2.index) < 2:
            continue
        xr = df2["xaxis"]
        maxval = df2["cumsum"].max()
        lp = ax.plot(
            xr,
            df2["cumsum"],
            lw=2,
            label=f"{yr} ({maxval:.0f})",
            drawstyle="steps-post",
        )
        # First row where we hit the max
        lrow = df2[df2["cumsum"] == maxval].iloc[0]
        ann.append(
            ax.text(
                lrow["xaxis"] + 1,
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
    lastdoy = df["xaxis"].max()
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
                # pylint: disable=protected-access
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
        labels = calendar.month_abbr[7:] + calendar.month_abbr[1:7]
        ax.set_xticklabels(labels)
    plot_common(ctx, ax)
    ax.set_ylim(bottom=0)
    ax.set_xlim(0, lastdoy)

    return fig, df.drop(columns=["xaxis"])


if __name__ == "__main__":
    plotter(
        {
            "limit": "yes",
            "station": "UNR",
            "opt": "state",
            "state": "IA",
            "c": "single",
            "phenomena": "SV",
            "significance": "W",
            "s": "jul1",
        }
    )
