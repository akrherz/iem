"""
This chart displays the number of products issued
by a NWS Office  or state by year for a given watch, warning,
or advisory of your choice.  These numbers are based on IEM archives and
are not official!  The counting is summing up distinct events.  If one
tornado watch covered 40 counties, this would only count as 1 for this
plot.

<p>Since the year 2005 and 2008 are common start years for VTEC tracking of
various phenomena, when this app encounters those years as the starting
point of the plot, they are droppped from the display.
"""

import datetime

import pandas as pd
from matplotlib.ticker import MaxNLocator
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import figure_axes
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {"yes": "Limit Plot to Year-to-Date", "no": "Plot Entire Year"}
PDICT2 = {
    "wfo": "View by Single NWS Forecast Office",
    "state": "View by State",
    "ugc": "NWS County/Forecast Zone",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="select",
            name="opt",
            default="wfo",
            options=PDICT2,
            label="What to summarize data by:",
        ),
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
            all=True,
        ),
        dict(type="state", default="IA", name="state", label="Select State:"),
        dict(
            type="ugc",
            name="ugc",
            default="IAC169",
            label="Select UGC Zone/County:",
        ),
        dict(
            type="select",
            name="limit",
            default="no",
            label="End Date Limit to Plot:",
            options=PDICT,
        ),
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
    limit = ctx["limit"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    opt = ctx["opt"]
    state = ctx["state"]

    ctx["_nt"].sts["_ALL"] = {"name": "All Offices"}
    params = {}
    if opt == "wfo":
        wfo_limiter = " and wfo = :wfo "
        params["wfo"] = station if len(station) == 3 else station[1:]
        if station == "_ALL":
            wfo_limiter = ""
        title1 = f"NWS {ctx['_nt'].sts[station]['name']}"
    elif opt == "ugc":
        wfo_limiter = " and ugc = :ugc "
        params["ugc"] = ctx["ugc"]
        name, wfo = get_ugc_name(ctx["ugc"])
        title1 = (
            f"NWS {ctx['_nt'].sts[wfo]['name']} Issued for [{ctx['ugc']}] "
            f"{name}"
        )
    else:
        wfo_limiter = " and substr(ugc, 1, 2) = :state "
        params["state"] = state
        title1 = state_names[state]
    doy_limiter = ""
    title = "Entire Year"
    if limit.lower() == "yes":
        title = f"thru ~{datetime.date.today():%-d %b}"
        doy_limiter = (
            " and extract(doy from issue) <= "
            "extract(doy from 'TODAY'::date) "
        )

    desc = "wfo, "
    if phenomena in ["TR", "HU"]:
        desc = ""
    if phenomena in ["SV", "TO"] and significance == "A":
        desc = ""
    params["sig"] = significance
    params["ph"] = phenomena
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
            with data as (
                SELECT distinct extract(year from issue)::int as yr,
                {desc} eventid
                from warnings where phenomena = :ph and significance = :sig
                {wfo_limiter} {doy_limiter})

            SELECT yr, count(*) from data GROUP by yr ORDER by yr ASC
        """
            ),
            conn,
            params=params,
        )
    if df.empty:
        if opt == "ugc":
            raise NoDataFound(
                "No events were found for this UGC + VTEC Phenomena\n"
                "combination, try flipping between county/zone"
            )
        raise NoDataFound("Sorry, no data found!")

    # Drop 2005 or 2008 if they are start years
    if df["yr"].min() == 2005:
        df = df[df["yr"] > 2005]
    elif df["yr"].min() == 2008:
        df = df[df["yr"] > 2008]
    title = (
        f"{title1} [{title}]\n"
        f"{vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance}) Count"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.bar(df["yr"], df["count"], align="center")
    ax.set_xlim(df["yr"].min() - 0.5, df["yr"].max() + 0.5)
    ymax = df["count"].max()
    ax.set_ylim(top=ymax * 1.2)
    for _, row in df.iterrows():
        ax.text(
            row["yr"],
            row["count"] + (ymax * 0.05),
            str(row["count"]),
            rotation=90,
            ha="center",
        )
    ax.grid(True)
    ax.set_ylabel("Yearly Count")
    xx = "" if limit == "yes" else datetime.date.today().year
    ax.set_xlabel(f"{xx} thru approximately {datetime.date.today():%-d %b}")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    return fig, df


if __name__ == "__main__":
    plotter({})
