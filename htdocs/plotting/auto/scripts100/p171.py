"""Distinct VTEC"""
import calendar

import numpy as np
from pandas.io.sql import read_sql
import seaborn as sns
import pyiem.nws.vtec as vtec
from pyiem import reference
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "wfo": "Select by NWS Forecast Office",
    "state": "Select by State",
    "ugc": "Select by NWS County/Forecast Zone",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart displays the monthly number of distinct
    NWS Office issued watch / warning / advisory product. For example, a
    single watch for a dozen counties would only count 1 in this chart. These
    values are based on unofficial archives maintained by the IEM.

    <p>If you select the state wide option, the totaling is a bit different. A
    single watch issued by multiple WFOs would potentially count as more than
    one event in this listing.  Sorry, tough issue to get around.  In the case
    of warnings and advisories, the totals should be good.</p>
    """
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
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    opt = ctx["opt"]
    state = ctx["state"]
    ctx["_nt"].sts["_ALL"] = {"name": "All Offices"}

    wfo_limiter = (" and wfo = '%s' ") % (
        station if len(station) == 3 else station[1:],
    )
    if station == "_ALL":
        wfo_limiter = ""
    if opt == "state":
        wfo_limiter = " and substr(ugc, 1, 2) = '%s'" % (state,)
    elif opt == "ugc":
        wfo_limiter = f" and ugc = '{ctx['ugc']}' "

    # NB we added a hack here that may lead to some false positives when events
    # cross over months, sigh, recall the 2017 eventid pain
    df = read_sql(
        f"""
        with data as (
            SELECT distinct
            extract(year from issue)::int as yr,
            extract(month from issue)::int as mo, wfo, eventid
            from warnings where phenomena = %s and significance = %s
            {wfo_limiter}
            GROUP by yr, mo, wfo, eventid)

        SELECT yr, mo, count(*) from data GROUP by yr, mo ORDER by yr, mo ASC
      """,
        pgconn,
        params=(phenomena, significance),
        index_col=None,
    )

    if df.empty:
        if opt == "ugc":
            raise NoDataFound(
                "No events were found for this UGC + VTEC Phenomena\n"
                "combination, try flipping between county/zone"
            )
        raise NoDataFound("Sorry, no data found!")

    df2 = df.pivot("yr", "mo", "count")
    df2 = df2.reindex(
        index=range(df["yr"].min(), df["yr"].max() + 1), columns=range(1, 13)
    )

    title = "NWS %s" % (ctx["_nt"].sts[station]["name"],)
    if opt == "state":
        title = ("NWS Issued for Counties/Zones for State of %s") % (
            reference.state_names[state],
        )
    elif opt == "ugc":
        name, wfo = get_ugc_name(ctx["ugc"])
        title = "NWS %s Issued for [%s] %s" % (
            ctx["_nt"].sts[wfo]["name"],
            ctx["ugc"],
            name,
        )
    subtitle = ("%s (%s.%s) Issued by Year, Month") % (
        vtec.get_ps_string(phenomena, significance),
        phenomena,
        significance,
    )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle)
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
    # Add some horizontal lines
    for i, year in enumerate(range(df["yr"].min(), df["yr"].max() + 1)):
        if year % 5 != 0:
            continue
        ax.axhline(i, zorder=3, lw=1, color="gray")
    # Add some vertical lines
    for i in range(1, 12):
        ax.axvline(i, zorder=3, lw=1, color="gray")
    ax.set_xticks(np.arange(12) + 0.5)
    ax.set_xticklabels(calendar.month_abbr[1:], rotation=0)
    ax.set_ylabel("Year")
    ax.set_xlabel("Month")

    return fig, df


if __name__ == "__main__":
    plotter(dict(wfo="OUN", network="WFO", phenomena="FG", significance="Y"))
