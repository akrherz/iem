"""
This chart shows the time partitioned frequency of having
at least one watch/warning/advisory (WWA) issued by the Weather Forecast
Office (top plot) and the overall number of WWA issued events
(bottom plot). This plot hopefully
answers the question of which day/week/month of the year is most common
to get a certain WWA type and which week has seen the most WWAs issued.
The plot
only considers issuance date. When plotting for a state, an event is
defined on a per forecast office basis.

<p><strong>Updated 4 Jan 2022:</strong> The week aggregation was
previously done by iso-week, which is sub-optimal.  The new aggregation
for week is by day of the year divided by 7.
"""
import calendar

import pandas as pd
from pyiem import reference
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

OPT = {
    "state": "Summarize by State",
    "wfo": "Summarize by NWS Forecast Office",
}
PDICT = {
    "doy": "Day of the Year",
    "week": "Week of the Year",
    "month": "Month of the Year",
}
OFFSETS = {
    "doy": 367,
    "week": 53,
    "month": 12,
}
PDICT2 = {
    "jan": "January 1",
    "jul": "July 1",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT,
            default="week",
            label="Partition By:",
            name="how",
        ),
        {
            "type": "select",
            "options": PDICT2,
            "default": "jan",
            "label": "Start plot on given date:",
            "name": "start",
        },
        dict(
            type="select",
            name="opt",
            options=OPT,
            default="wfo",
            label="How to Spatially Group Statistics:",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State (if appropriate):",
        ),
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO (if appropriate):",
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
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    opt = ctx["opt"]
    state = ctx["state"][:2]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    station = ctx["station"][:4]
    params = {
        "ph": phenomena,
        "sig": significance,
        "wfo": station,
    }
    limiter = " wfo = :wfo "
    title = f"[{station}] NWS {ctx['_nt'].sts[station]['name']}"
    if opt == "state":
        title = f"State of {reference.state_names[state]}"
        limiter = " substr(ugc, 1, 2) = :state "
        params["state"] = state
    agg = f"extract({ctx['how']} from issue)"
    if ctx["how"] == "week":
        agg = "(extract(doy from issue) / 7)::int"
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
        with obs as (
            SELECT distinct extract(year from issue) as yr,
            {agg} as datum, wfo, eventid
            from warnings WHERE
            {limiter} and phenomena = :ph and significance = :sig
        )
        SELECT yr::int, datum, count(*) from obs GROUP by yr, datum
        ORDER by yr ASC
        """
            ),
            conn,
            params=params,
            index_col=None,
        )

    if df.empty:
        raise NoDataFound("ERROR: No Results Found!")

    # Top Panel: count
    title = (
        f"{title}\n"
        f"{vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance}) Events - {df['yr'].min():.0f} to "
        f"{df['yr'].max():.0f}"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1, sharex=True)
    gdf = (
        df[["datum", "count"]]
        .groupby("datum")
        .agg(
            years=pd.NamedAgg(column="count", aggfunc="count"),
            count=pd.NamedAgg(column="count", aggfunc="sum"),
        )
        .copy()
    )
    # Duplicate gdf so that we can plot centered on 1 July
    gdf2 = (
        gdf.reset_index()
        .assign(datum=lambda x: x["datum"] + OFFSETS[ctx["how"]])
        .set_index("datum")
    )
    gdf = pd.concat([gdf, gdf2])
    df = df.rename(columns={"datum": ctx["how"]})
    width = 0.8
    xticks = []
    xticklabels = []
    if ctx["how"] == "week":
        gdf.index = gdf.index.values * 7
        width = 6.5
    if ctx["how"] in ["doy", "week"]:
        for i, dt in enumerate(pd.date_range("2000/1/1", "2001/12/31")):
            if dt.day == 1:
                xticks.append(i + 1)
                xticklabels.append(dt.strftime("%b"))
    else:
        xticks = range(1, 25)
        xticklabels = calendar.month_abbr[1:] + calendar.month_abbr[1:]

    ax[0].bar(gdf.index.values, gdf["years"], width=width)
    ax[0].grid()
    ax[0].set_ylabel("Years with 1+ Event")

    # Bottom Panel: events
    ax[1].bar(gdf.index.values, gdf["count"], width=width)
    ax[1].set_ylabel("Total Event Count")
    ax[1].grid()
    ax[1].set_xlabel(f"Partitioned by {PDICT[ctx['how']]}")
    ax[1].set_xticks(xticks)
    ax[1].set_xticklabels(xticklabels)
    # sharex is on
    if ctx["start"] == "jul":
        if ctx["how"] in ["doy", "week"]:
            ax[1].set_xlim(183, 183 + 365)
        else:
            ax[1].set_xlim(6.5, 18.5)
    else:
        ax[1].set_xlim(
            0 if ctx["how"] == "month" else -6.5,
            13 if ctx["how"] == "month" else 366,
        )

    return fig, df


if __name__ == "__main__":
    plotter({})
