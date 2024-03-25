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

<p><strong>Updated 21 Nov 2023:</strong> An experimental attempt is now
included on the plot to estimate the climatological favored period for the
given event type.  This algorithm is experimental and attempts to make life
choices on if it thinks the climatology is bimodal or not.  Feedback welcome!
"""

import calendar

import pandas as pd
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
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


def compute_plot_climo(ax, df):
    """Figure out the climatology."""
    # Our data frame is by week of the year
    # Our test for bimodal is if the top 5 weeks have a intermediate
    # value less than 50% of the top week
    df2 = df.sort_values(by="count", ascending=False).head(5)
    df3 = df.loc[df2.index.min() : df2.index.max() + 1]
    bimodal = df3["count"].max() > (df3["count"].min() * 2)

    # Figure out the indicies that should contain our climos
    idx1 = df2.index[0]
    idx2 = None
    if bimodal:
        # pick the furthest week from the top week
        maxdist = 0
        for idx in df2.index:
            dist = abs(idx - idx1)
            if dist > maxdist:
                maxdist = dist
                idx2 = idx
    # apply a 80/20 rule, attempting to minimize number of weeks to find
    # 80% of the events
    threshold = df["count"].sum() * (0.3 if bimodal else 0.8)
    ymax = df["count"].max()
    hits = 0
    for weeks in range(4, 44):
        rolsum = df["count"].rolling(window=weeks, center=False).sum()
        if rolsum.max() < threshold:
            continue
        df2 = df[rolsum == rolsum.max()]
        # clear some space to plot the climo
        ax.set_ylim(0, ymax * 1.3)
        left = df2.index[0] - (weeks * 7)
        if hits == 1 and bimodal and (left > idx2 or idx2 > df2.index[0]):
            continue
        if idx2 is not None and hits == 1 and left <= idx1 <= df2.index[0]:
            return
        ax.barh(
            ymax * 1.1,
            weeks * 7,
            left=left,
            height=(ymax * 0.12),
            color="tan",
            label=None if hits > 0 else "Favored Season",
        )
        ax.text(
            left + (weeks * 7) / 2.0,
            ymax * 1.1,
            f"{weeks} Weeks\n"
            f"{rolsum.max() / df['count'].sum() * 100.:.0f}% Events",
            ha="center",
            va="center",
        )
        if hits == 0:
            ax.legend(loc=(0.8, 1.01))
        hits += 1
        if not bimodal or hits == 2:
            return


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
    # We need to fill in missing values
    if ctx["how"] == "doy":
        gdf = gdf.reindex(range(1, 367), fill_value=0)
    elif ctx["how"] == "week":
        gdf = gdf.reindex(range(0, 53), fill_value=0)
    elif ctx["how"] == "month":
        gdf = gdf.reindex(range(1, 13), fill_value=0)
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

    if ctx["how"] == "week":
        if ctx["start"] == "jul":
            compute_plot_climo(ax[1], gdf.iloc[26:79])  # only send 1 year
        else:
            compute_plot_climo(ax[1], gdf.iloc[:53])  # only send 1 year
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
