"""
This chart presents the total number of Local Storm Reports disseminated by the
NWS by month and year.

<p><a href="/plotting/auto/?q=171">Autoplot 171</a> produces a similar plot,
but contains totals of Watch, Warnings, and Advisories issued.</p>
"""
import calendar

import numpy as np
import pandas as pd
import seaborn as sns
from pyiem import reference
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn, get_sqlalchemy_conn
from sqlalchemy import text

MDICT = {
    "NONE": "All LSR Types",
    "NRS": "All LSR Types except HEAVY RAIN + SNOW",
    "H1": "One Inch and Larger Hail ",
    "H2": "Two Inch and Larger Hail ",
    "G58": "Thunderstorm Wind Gust >= 58 MPH ",
    "G75": "Thunderstorm Wind Gust >= 75 MPH ",
    "CON": "Convective LSRs (Tornado, TStorm Gst/Dmg, Hail)",
    "AVALANCHE": "AVALANCHE",
    "BLIZZARD": "BLIZZARD",
    "COASTAL FLOOD": "COASTAL FLOOD",
    "DEBRIS FLOW": "DEBRIS FLOW",
    "DENSE FOG": "DENSE FOG",
    "DOWNBURST": "DOWNBURST",
    "DUST STORM": "DUST STORM",
    "EXCESSIVE HEAT": "EXCESSIVE HEAT",
    "EXTREME COLD": "EXTREME COLD",
    "EXTR WIND CHILL": "EXTR WIND CHILL",
    "FLASH FLOOD": "FLASH FLOOD",
    "FLOOD": "FLOOD",
    "FOG": "FOG",
    "FREEZE": "FREEZE",
    "FREEZING DRIZZLE": "FREEZING DRIZZLE",
    "FREEZING RAIN": "FREEZING RAIN",
    "FUNNEL CLOUD": "FUNNEL CLOUD",
    "HAIL": "HAIL",
    "HEAVY RAIN": "HEAVY RAIN",
    "HEAVY SLEET": "HEAVY SLEET",
    "HEAVY SNOW": "HEAVY SNOW",
    "HIGH ASTR TIDES": "HIGH ASTR TIDES",
    "HIGH SURF": "HIGH SURF",
    "HIGH SUST WINDS": "HIGH SUST WINDS",
    "HURRICANE": "HURRICANE",
    "ICE STORM": "ICE STORM",
    "LAKESHORE FLOOD": "LAKESHORE FLOOD",
    "LIGHTNING": "LIGHTNING",
    "LOW ASTR TIDES": "LOW ASTR TIDES",
    "MARINE TSTM WIND": "MARINE TSTM WIND",
    "NON-TSTM WND DMG": "NON-TSTM WND DMG",
    "NON-TSTM WND GST": "NON-TSTM WND GST",
    "RAIN": "RAIN",
    "RIP CURRENTS": "RIP CURRENTS",
    "SLEET": "SLEET",
    "SNOW": "SNOW",
    "STORM SURGE": "STORM SURGE",
    "TORNADO": "TORNADO",
    "TROPICAL STORM": "TROPICAL STORM",
    "TSTM WND DMG": "TSTM WND DMG",
    "TSTM WND GST": "TSTM WND GST",
    "WALL CLOUD": "WALL CLOUD",
    "WATER SPOUT": "WATER SPOUT",
    "WILDFIRE": "WILDFIRE",
}
PDICT = {
    "wfo": "Select by NWS Forecast Office",
    "state": "Select by State",
    "ugc": "Select by NWS County/Forecast Zone",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="select",
            name="opt",
            default="wfo",
            options=PDICT,
            label="How to summarize the data?",
        ),
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
            all=True,
        ),
        dict(type="state", name="state", default="IA", label="Select State:"),
        dict(
            type="ugc",
            name="ugc",
            default="IAC169",
            label="Select UGC Zone/County:",
        ),
        dict(
            type="select",
            name="filter",
            default="NONE",
            options=MDICT,
            label="Local Storm Report Type Filter",
        ),
        dict(type="cmap", name="cmap", default="Greens", label="Color Ramp:"),
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
    station = ctx["station"]
    opt = ctx["opt"]
    state = ctx["state"]
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    myfilter = ctx["filter"]
    if myfilter == "NONE":
        tlimiter = ""
    elif myfilter == "NRS":
        tlimiter = " and typetext not in ('HEAVY RAIN', 'SNOW', 'HEAVY SNOW') "
    elif myfilter == "H1":
        tlimiter = " and typetext = 'HAIL' and magnitude >= 1 "
    elif myfilter == "H2":
        tlimiter = " and typetext = 'HAIL' and magnitude >= 2 "
    elif myfilter == "G58":
        tlimiter = " and type = 'G' and magnitude >= 58 "
    elif myfilter == "G75":
        tlimiter = " and type = 'G' and magnitude >= 75 "
    elif myfilter == "CON":
        tlimiter = (
            " and typetext in ('TORNADO', 'HAIL', 'TSTM WND GST', "
            "'TSTM WND DMG') "
        )
    else:
        tlimiter = f" and typetext = '{myfilter}' "
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    params = {
        "tzname": ctx["_nt"].sts[station]["tzname"],
    }
    wfo_limiter = " and wfo = :wfo "
    params["wfo"] = station if len(station) == 3 else station[1:]
    if station == "_ALL":
        wfo_limiter = ""
        ctx["_sname"] = "All Offices"
    if opt == "state":
        wfo_limiter = " and state = :state "
        params["state"] = state
    elif opt == "ugc":
        wfo_limiter = " and ugc = :ugc "
        params["ugc"] = ctx["ugc"]
    with get_sqlalchemy_conn("postgis") as conn:
        if opt != "ugc":
            daily = pd.read_sql(
                text(
                    f"""
                     with data as (
                SELECT distinct valid, geom, typetext, magnitude
                from lsrs l where 1 = 1 {tlimiter} {wfo_limiter}
                ) select date(valid at time zone :tzname),
                count(*) from data GROUP by date ORDER by date
            """
                ),
                conn,
                params=params,
                index_col=None,
                parse_dates="date",
            )
        else:
            daily = pd.read_sql(
                text(
                    f"""
                with data as (
                SELECT distinct valid, geom, typetext, magnitude
                from lsrs l JOIN ugcs u on (l.gid = u.gid)
                where 1 = 1 {tlimiter} {wfo_limiter}
                )
                select date(valid at time zone :tzname), count(*)
                from data GROUP by date ORDER by date
            """
                ),
                conn,
                index_col=None,
                params=params,
                parse_dates="date",
            )
    if daily.empty:
        raise NoDataFound("No data found for query.")
    daily["yr"] = daily["date"].dt.year
    daily["mo"] = daily["date"].dt.month
    df = daily[["yr", "mo", "count"]].groupby(["yr", "mo"]).sum().reset_index()

    df2 = df.pivot(index="yr", columns="mo", values="count").reindex(
        index=range(df["yr"].min(), df["yr"].max() + 1),
        columns=range(1, 13),
    )

    title = f"NWS {ctx['_sname']}"
    if opt == "state":
        title = (
            "NWS Local Storm Reports for State of "
            f"{reference.state_names[state]}"
        )
    elif opt == "ugc":
        name, wfo = get_ugc_name(ctx["ugc"])
        title = (
            f"NWS [{wfo}] {ctx['_nt'].sts[wfo]['name']} Reports for "
            f"[{ctx['ugc']}] {name}"
        )
    (fig, ax) = figure_axes(
        title=title,
        subtitle=f"Local Storm Reports (LSRs): {MDICT[myfilter]}",
        apctx=ctx,
    )
    # Print the top 10 days
    ypos = 0.9
    fig.text(0.82, ypos, "Top 10 Dates")
    ypos -= 0.04
    fig.text(0.82, ypos, params["tzname"])
    for _, row in (
        daily.sort_values("count", ascending=False).head(10).iterrows()
    ):
        ypos -= 0.04
        fig.text(0.82, ypos, f"{row['date']:%Y-%m-%d} {row['count']:3.0f}")
    ax.set_position([0.1, 0.1, 0.75, 0.8])
    g = sns.heatmap(
        df2,
        annot=True,
        fmt=".0f",
        linewidths=0.5,
        ax=ax,
        vmin=1,
        cmap=ctx["cmap"],
        zorder=2,
    )
    g.set_yticklabels(g.get_yticklabels(), rotation=0)
    # Add sums to RHS
    sumdf = df2.sum(axis="columns").fillna(0)
    for year, count in sumdf.items():
        ax.text(12, year, f"{count:.0f}")
    # Add some horizontal lines
    for i, year in enumerate(range(df["yr"].min(), df["yr"].max() + 1)):
        ax.text(
            12 + 0.7, i + 0.5, f"{sumdf[year]:4.0f}", ha="right", va="center"
        )
        if year % 5 != 0:
            continue
        ax.axhline(i, zorder=3, lw=1, color="gray")
    ax.text(1.0, -0.02, "Total", transform=ax.transAxes)
    # Add some vertical lines
    for i in range(1, 12):
        ax.axvline(i, zorder=3, lw=1, color="gray")
    ax.set_xticks(np.arange(12) + 0.5)
    ax.set_xticklabels(calendar.month_abbr[1:], rotation=0)
    ax.set_ylabel("Year")
    ax.set_xlabel("Month")

    return fig, df


if __name__ == "__main__":
    plotter({})
