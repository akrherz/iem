"""
This autoplot prints out the top 10 dates for number of VTEC events issued.
Note that a warning covering multiple counties would only count as 1 in this
summary.  You can either produce top 10 totals for a given wfo/state or get the
top 10 totals per wfo/state over all wfos/states.

<p>If you summarize by a 12z to 12z period, the date of the start of the period
is shown. If you summarize over a multiple day period, the entire period must
reside within any calendar date limit.</p>

<p><a href="/plotting/auto/?q=171">Autoplot 171</a> is similar to this app, but
produces monthly heatmaps.
"""

from datetime import date

import pandas as pd
import pyiem.nws.vtec as vtec
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot import ARG_FEMA, FEMA_REGIONS, fema_region2states
from iemweb.util import month2months

MDICT = {
    "all": "Entire Year",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "octmar": "October thru March",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}
DDICT = {
    "cal": "Local Calendar Day for Office",
    "12z": "12 UTC to 12 UTC Period",
}
PDICT = {
    "wfo": "Select by NWS Forecast Office",
    "state": "Select by State",
    "fema": "Select by FEMA Region",
    "all": "Show NWS Totals (all)",
    "bywfo": "Show per NWS Office Totals",
    "bystate": "Show per State Totals",
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
        {
            "type": "select",
            "options": DDICT,
            "default": "cal",
            "label": "Define what a day means",
            "name": "day",
        },
        {
            "type": "int",
            "name": "days",
            "default": 1,
            "label": "Number of Days to Summarize (1-31)",
            "gt": 1,
            "lt": 32,
        },
        dict(
            type="select",
            name="month",
            default="all",
            label="Month(s) Limiter",
            options=MDICT,
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
        ARG_FEMA,
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
    ]
    return desc


def compute_dates(months: list, dt: date, days: int):
    """Figure out how to represent this period, since the end may out."""
    end_dt = dt + pd.Timedelta(days=days - 1)
    default = f"{dt:%d %b} - {end_dt:%d %b %Y}"
    if end_dt.month in months:
        return default
    for _dt in pd.date_range(dt, end_dt):
        if _dt.month not in months:
            break
        if _dt == dt:
            default = f"{dt:%d %b %Y}"
        else:
            default = f"{dt:%d %b} - {_dt:%d %b %Y}"
    return default


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    opt = ctx["opt"]
    if opt == "all":
        opt = "wfo"
        station = "_ALL"
    state = ctx["state"]
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    month = ctx["month"]
    months = month2months(month)
    params = {
        "ph": [
            phenomena,
        ],
        "sig": significance,
        "tzname": ctx["_nt"].sts[station]["tzname"],
    }
    offset = ""
    tt = "by Calendar Date"
    if ctx["day"] == "12z":
        params["tzname"] = "UTC"
        offset = " - '12 hours'::interval "
        tt = "by 12z-12z Period"
    wfo_limiter = " and wfo = :wfo "
    params["wfo"] = station if len(station) == 3 else station[1:]
    if station == "_ALL":
        wfo_limiter = ""
        ctx["_sname"] = "All Offices"
    if opt == "state":
        wfo_limiter = " and substr(ugc, 1, 2) = :state "
        params["state"] = state
    elif opt == "fema":
        wfo_limiter = " and substr(ugc, 1, 2) = ANY(:states) "
        params["states"] = fema_region2states(ctx["fema"])
    if opt in ["bystate", "bywfo"]:
        wfo_limiter = ""

    subtitle = (
        f"{vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance})"
    )
    if ctx["c"] == "svrtor":
        params["ph"] = ["SV", "TO"]
        params["sig"] = "W"
        subtitle = "Severe T'Storm + Tornado Warnings"
    elif ctx["c"] == "svrtorffw":
        params["ph"] = ["SV", "TO", "FF"]
        params["sig"] = "W"
        subtitle = "Svr T'Storm + Tornado + Flash Flood Warnings"

    sql = f"""
        SELECT
        vtec_year as yr,
        extract(month from issue)::int as mo,
        min(date(issue at time zone :tzname {offset})) as min_date,
        wfo, phenomena, significance, eventid
        from warnings where phenomena = ANY(:ph) and significance = :sig
        {wfo_limiter}
        GROUP by yr, mo, wfo, phenomena, significance, eventid
        ORDER by yr asc, mo asc
    """
    if opt == "bystate":
        # Yes, double counting
        sql = f"""
            SELECT
            vtec_year as yr,
            extract(month from issue)::int as mo,
            min(date(issue at time zone :tzname {offset})) as min_date,
            substr(ugc, 1, 2) as state,
            wfo, phenomena, significance, eventid
            from warnings where phenomena = ANY(:ph) and significance = :sig
            GROUP by yr, mo, state, wfo, phenomena, significance, eventid
            ORDER by yr asc, mo asc
        """
    with get_sqlalchemy_conn("postgis") as conn:
        # NB quasi hack here as we have some redundant ETNs for a given year
        # so the groupby helps some.
        daily = pd.read_sql(
            sql_helper(sql),
            conn,
            params=params,
            index_col=None,
            parse_dates="min_date",
        )

    if daily.empty:
        raise NoDataFound("Sorry, no data found!")
    daily = daily[daily["mo"].isin(months)].sort_values(
        "min_date", ascending=True
    )
    if daily.empty:
        raise NoDataFound("Sorry, no data found for given months.")
    if opt in ["bystate", "bywfo"]:
        col = opt.replace("by", "")
        df = (
            daily[["min_date", "eventid", col]]
            .groupby([col, "min_date"])
            .count()
            .reset_index()
            .rename(columns={"eventid": "count"})
            .sort_values(["count", "min_date"], ascending=False)
            .copy()
        )
    else:
        df = (
            daily[["min_date", "eventid"]]
            .groupby("min_date")
            .count()
            .reset_index()
            .rename(columns={"eventid": "count"})
            .sort_values(["count", "min_date"], ascending=False)
            .copy()
        )
    if ctx["days"] > 1:
        # We need to undo the sort and reindex to include all days
        df = (
            df.set_index("min_date")
            .reindex(
                pd.date_range(
                    start=daily["min_date"].min(),
                    end=daily["min_date"].max(),
                    freq="D",
                    name="min_date",
                )
            )
            .fillna(0)
            .rolling(ctx["days"], min_periods=1)
            .sum()
            .reset_index()
            .sort_values(["count", "min_date"], ascending=False)
        )

    title = f"NWS {ctx['_sname']}"
    if opt == "state":
        title = (
            "NWS Issued for Counties/Zones for State of "
            f"{reference.state_names[state]}"
        )
    elif opt == "bystate":
        title = "NWS Issued by State"
    elif opt == "bywfo":
        title = "NWS Issued by WFO"
    elif opt == "fema":
        title = f"NWS Issued by FEMA {FEMA_REGIONS[ctx['fema']]}"
    if ctx["days"] > 1:
        title += f" [{ctx['days']} Day Sum]"
    if month != "all":
        title += f" [{MDICT[month]}]"
    fig = figure(
        title=title,
        subtitle=(
            f"{subtitle} Events {tt} [{daily['min_date'].min():%d %b %Y}-"
            f"{daily['min_date'].max():%d %b %Y}]"
        ),
        apctx=ctx,
    )
    ax = fig.add_axes((0.3, 0.1, 0.5, 0.8))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    df2 = df.iloc[:10]
    ax.barh(
        range(1, len(df2.index) + 1),
        df2["count"].values,
    )
    labels = []
    rank = 0
    lastval = -1
    extra = ""
    for _, row in df.head(10).iterrows():
        if row["count"] != lastval:
            rank += 1
        lastval = row["count"]
        md = f"{row['min_date']:%d %b %Y}"
        if ctx["days"] > 1:
            # Life choices here about what happens when the period crosses
            # a month boundary
            md = compute_dates(months, row["min_date"], ctx["days"])
        if opt in ["bystate", "bywfo"]:
            extra = row[opt.replace("by", "")]
        labels.append(f"#{rank} {extra} {md} :: {row['count']:.0f}")
    ax.set_yticks(range(1, len(df2.index) + 1))
    ax.set_yticklabels(labels)
    ax.set_ylim(len(df2.index) + 1, 0)
    ax.set_xlabel(f"Event Count by Date: {params['tzname']}")

    return fig, df
