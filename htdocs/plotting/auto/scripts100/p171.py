"""
This chart displays the monthly number of distinct
NWS Office issued watch / warning / advisory product. For example, a
single watch for a dozen counties would only count 1 in this chart. These
values are based on unofficial archives maintained by the IEM.

<p>The chart summarizes by the month of issuance, so long fuse products like
Flood Warnings that cover multiple months in time would only appear once for
the month of issuance.</p>

<p>If you select the state wide option, the totaling is a bit different. A
single watch issued by multiple WFOs would potentially count as more than
one event in this listing.  Sorry, tough issue to get around.  In the case
of warnings and advisories, the totals should be good.</p>

<p><a href="/plotting/auto/?q=245">Autoplot 245</a> produces a similar plot to
this one, but with Local Storm Report (LSR) totals.</p>
"""

import calendar

import numpy as np
import pandas as pd
import pyiem.nws.vtec as vtec
import seaborn as sns
from pyiem import reference
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn, get_sqlalchemy_conn
from sqlalchemy import text

PDICT = {
    "wfo": "Select by NWS Forecast Office",
    "state": "Select by State",
    "ugc": "Select by NWS County/Forecast Zone",
}
PDICT2 = {
    "single": "Total for Single Selected Phenomena / Significance",
    "svrtor": "Severe T'Storm + Tornado Warnings",
    "svrtorffw": "Severe T'Storm + Tornado + Flash Flood Warnings",
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
        {
            "type": "select",
            "options": PDICT2,
            "name": "c",
            "default": "single",
            "label": "Total by Selected Phenomena/Significance or Combo",
        },
        dict(
            type="phenomena",
            name="phenomena",
            default="FF",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="W",
            label="Select Watch/Warning Significance Level:",
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
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    opt = ctx["opt"]
    state = ctx["state"]
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }

    params = {
        "ph": [
            phenomena,
        ],
        "sig": significance,
        "tzname": ctx["_nt"].sts[station]["tzname"],
    }
    wfo_limiter = " and wfo = :wfo "
    params["wfo"] = station if len(station) == 3 else station[1:]
    if station == "_ALL":
        wfo_limiter = ""
        ctx["_sname"] = "All Offices"
    if opt == "state":
        wfo_limiter = " and substr(ugc, 1, 2) = :state "
        params["state"] = state
    elif opt == "ugc":
        wfo_limiter = " and ugc = :ugc "
        params["ugc"] = ctx["ugc"]

    subtitle = (
        f"{vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance}) Issued by Year, Month"
    )
    if ctx["c"] == "svrtor":
        params["ph"] = ["SV", "TO"]
        params["sig"] = "W"
        subtitle = "Severe T'Storm + Tornado Warnings Issued by Year, Month"
    elif ctx["c"] == "svrtorffw":
        params["ph"] = ["SV", "TO", "FF"]
        params["sig"] = "W"
        subtitle = (
            "Svr T'Storm + Tornado + Flash Flood Warnings "
            "Issued by Year, Month"
        )

    with get_sqlalchemy_conn("postgis") as conn:
        # NB quasi hack here as we have some redundant ETNs for a given year
        # so the groupby helps some.
        daily = pd.read_sql(
            text(
                f"""
                SELECT
                extract(year from issue)::int as yr,
                extract(month from issue)::int as mo,
                min(date(issue at time zone :tzname)) as min_date,
                wfo,
                phenomena, significance, eventid
                from warnings where phenomena = ANY(:ph)
                and significance = :sig
                {wfo_limiter}
                GROUP by yr, mo, wfo, phenomena, significance, eventid
                ORDER by yr asc, mo asc
        """
            ),
            conn,
            params=params,
            index_col=None,
        )

    if daily.empty:
        if opt == "ugc":
            raise NoDataFound(
                "No events were found for this UGC + VTEC Phenomena\n"
                "combination, try flipping between county/zone"
            )
        raise NoDataFound("Sorry, no data found!")
    df = (
        daily[["yr", "mo", "eventid"]]
        .groupby(["yr", "mo"])
        .count()
        .reset_index()
        .rename(columns={"eventid": "count"})
    )

    df2 = df.pivot(index="yr", columns="mo", values="count").reindex(
        index=range(df["yr"].min(), df["yr"].max() + 1),
        columns=range(1, 13),
    )

    title = f"NWS {ctx['_sname']}"
    if opt == "state":
        title = (
            "NWS Issued for Counties/Zones for State of "
            f"{reference.state_names[state]}"
        )
    elif opt == "ugc":
        name, wfo = get_ugc_name(ctx["ugc"])
        title = (
            f"NWS [{wfo}] {ctx['_nt'].sts[wfo]['name']} Issued for "
            f"[{ctx['ugc']}] {name}"
        )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    # Print the top 10 days
    ypos = 0.9
    fig.text(0.82, ypos, "Top 10 Dates")
    ypos -= 0.04
    fig.text(0.82, ypos, params["tzname"])
    gdf = daily.groupby("min_date").count().sort_values("yr", ascending=False)
    for dt, row in gdf.head(10).iterrows():
        ypos -= 0.04
        fig.text(0.82, ypos, f"{dt} {row['yr']:3.0f}")
    ax.set_position([0.1, 0.1, 0.75, 0.8])
    sns.heatmap(
        df2,
        annot=True,
        fmt=".0f",
        linewidths=0.5,
        ax=ax,
        vmin=1,
        cmap=ctx["cmap"],
        zorder=2,
    )
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
    plotter(
        {
            "wfo": "BOX",
            "network": "WFO",
            "phenomena": "SV",
            "significance": "W",
        }
    )
