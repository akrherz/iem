"""
This chart presents a histogram of the Watch,
Warning, Advisory valid time.  This is the time period between the
issuance and final expiration time of a given event.  An individual event
is one Valid Time Event Code (VTEC) event identifier.  For example, a
Winter Storm Watch for 30 counties would only count as one event in this
analysis.

<p>If an individual event goes for more than 24 hours, the event is
capped at a 24 hour duration for the purposes of this analysis.  Events
like Flood Warnings are prime examples of this.

<p><a href="/plotting/auto/?q=48">Autoplot 48</a> is similar to this, but
plots for a single county/zone/parish at a time.
"""

import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text

MDICT = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
    "spring2": "Spring (AMJ)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
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


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        dict(
            type="phenomena",
            name="phenomena",
            default="WC",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="W",
            label="Select Watch/Warning Significance Level:",
        ),
        dict(
            type="select",
            name="season",
            default="all",
            label="Select Time Period:",
            options=MDICT,
        ),
    ]
    return desc


def get_data(conn, params):
    """Fetch me the data."""
    monthlimiter = "and extract(month from issue) = ANY(:months)"
    if params["months"] is None:
        monthlimiter = ""
    df = pd.read_sql(
        text(
            f"""
    WITH data as (
        SELECT extract(year from issue) as yr, eventid,
        min(issue at time zone :tzname) as minissue,
        max(issue at time zone :tzname) as maxissue,
        max(expire at time zone :tzname) as maxexpire from warnings WHERE
        phenomena = :phenomena and significance = :significance
        and wfo = :wfo {monthlimiter} GROUP by yr, eventid),
    events as (
        select count(*), min(minissue) as min_issue,
        max(maxissue) as max_issue from data),
    timedomain as (
        SELECT generate_series(minissue,
            least(maxexpire, minissue + '24 hours'::interval)
            , '1 minute'::interval)
        as ts from data
    ),
    data2 as (
        SELECT
        extract(hour from ts)::int * 60 + extract(minute from ts)::int
        as minute, count(*) from timedomain
        GROUP by minute ORDER by minute ASC)
    select d.minute, d.count, e.count as total, min_issue, max_issue
    from data2 d, events e
    """
        ),
        conn,
        params=params,
        index_col="minute",
    )
    if not df.empty:
        df = df.reindex(range(24 * 60))
        df["frequency"] = df["count"] / df["total"] * 100.0
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    wfo = ctx["station"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    if ctx["season"] == "all":
        months = list(range(1, 13))
    elif ctx["season"] == "spring":
        months = [3, 4, 5]
    elif ctx["season"] == "spring2":
        months = [4, 5, 6]
    elif ctx["season"] == "fall":
        months = [9, 10, 11]
    elif ctx["season"] == "summer":
        months = [6, 7, 8]
    elif ctx["season"] == "winter":
        months = [12, 1, 2]
    else:
        ts = datetime.datetime.strptime(f"2000-{ctx['season']}-01", "%Y-%b-%d")
        months = [ts.month]

    tzname = ctx["_nt"].sts[wfo]["tzname"]
    dfseason = None
    sfcol = f"{ctx['season']}_frequency"
    with get_sqlalchemy_conn("postgis") as conn:
        dfall = get_data(
            conn,
            {
                "tzname": tzname,
                "phenomena": phenomena,
                "significance": significance,
                "wfo": wfo,
                "months": None,
            },
        )
        if dfall.empty:
            raise NoDataFound("No Results Found")
        if ctx["season"] != "all":
            dfseason = get_data(
                conn,
                {
                    "tzname": tzname,
                    "phenomena": phenomena,
                    "significance": significance,
                    "wfo": wfo,
                    "months": months,
                },
            )
            dfall[sfcol] = dfseason["frequency"]
            subtitle = f"All Year + {MDICT[ctx['season']]}"
        else:
            dfall[sfcol] = -1
            subtitle = "All Year"
    title = (
        f"{ctx['_sname']} :: Time of Day Frequency of "
        f"{vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance})"
    )
    subtitle = (
        f"{subtitle}, Period: "
        f"{dfall['min_issue'].min():%d %b %Y} - "
        f"{dfall['max_issue'].max():%d %b %Y}"
    )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    ax.bar(
        dfall.index.values,
        dfall["frequency"].values,
        color="tan",
        align="center",
        label="All Year",
        width=1,
    )
    ax.grid()
    if dfseason is not None:
        ax.plot(
            dfall.index.values,
            dfall[sfcol].values,
            drawstyle="steps-pre",
            label=MDICT[ctx["season"]],
            lw=2,
            color="b",
        )
        ax.legend(loc="best")
    if max(dfall["frequency"].max(), dfall[sfcol].max()) > 70:
        ax.set_ylim(0, 101)
    ax.set_xticks(range(0, 25 * 60, 60))
    ax.set_xlim(-0.5, 24 * 60 + 1)
    ax.set_xticklabels(
        [
            "Mid",
            "",
            "",
            "3 AM",
            "",
            "",
            "6 AM",
            "",
            "",
            "9 AM",
            "",
            "",
            "Noon",
            "",
            "",
            "3 PM",
            "",
            "",
            "6 PM",
            "",
            "",
            "9 PM",
            "",
            "",
            "Mid",
        ]
    )
    ax.set_xlabel(f"Timezone: {tzname} (Daylight or Standard)")
    ylabel = f"{dfall['total'].max()} Overall"
    if ctx["season"] != "all":
        ylabel += f", {dfseason['total'].max()} {MDICT[ctx['season']]}"
    ax.set_ylabel(f"Percentage [%] out of\n{ylabel} Events")

    return fig, dfall.drop(columns=["min_issue", "max_issue"])
