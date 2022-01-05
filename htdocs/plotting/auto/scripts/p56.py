"""WWA Frequency"""
import calendar
import datetime

from pandas.io.sql import read_sql
from pyiem.nws import vtec
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot import figure
from pyiem import reference
from pyiem.exceptions import NoDataFound

OPT = {
    "state": "Summarize by State",
    "wfo": "Summarize by NWS Forecast Office",
}
PDICT = {
    "doy": "Day of the Year",
    "week": "Week of the Year",
    "month": "Month of the Year",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart shows the time partitioned frequency of having
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
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT,
            default="week",
            label="Partition By:",
            name="how",
        ),
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
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())

    opt = ctx["opt"]
    state = ctx["state"][:2]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    station = ctx["station"][:4]

    limiter = f" wfo = '{station}' "
    title = f"[{station}] NWS {ctx['_nt'].sts[station]['name']}"
    if opt == "state":
        title = f"State of {reference.state_names[state]}"
        limiter = f" substr(ugc, 1, 2) = '{state}' "
    agg = f"extract({ctx['how']} from issue)"
    if ctx["how"] == "week":
        agg = "(extract(doy from issue) / 7)::int"
    df = read_sql(
        f"""
    with obs as (
        SELECT distinct extract(year from issue) as yr,
        {agg} as datum, wfo, eventid
        from warnings WHERE
        {limiter} and phenomena = %s and significance = %s
    )
    SELECT yr::int, datum, count(*) from obs GROUP by yr, datum ORDER by yr ASC
    """,
        pgconn,
        params=(phenomena, significance),
        index_col=None,
    )

    if df.empty:
        raise NoDataFound("ERROR: No Results Found!")
    df = df.rename(columns={"datum": ctx["how"]})

    # Top Panel: count
    title = (
        f"{title}\n"
        f"{vtec.get_ps_string(phenomena, significance)} "
        f"({phenomena}.{significance}) Events - {df['yr'].min():.0f} to "
        f"{df['yr'].max():.0f}"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1, sharex=True)
    gdf = df.groupby(ctx["how"]).count()
    xaxis = gdf.index.values
    width = 1
    xticks = []
    if ctx["how"] == "week":
        xaxis = gdf.index.values * 7
        width = 7
    if ctx["how"] in ["doy", "week"]:
        sts = datetime.datetime(2012, 1, 1)
        for i in range(1, 13):
            ts = sts.replace(month=i)
            xticks.append(int(ts.strftime("%j")))
    else:
        xticks = range(1, 13)

    ax[0].bar(xaxis, gdf["yr"], width=width)
    ax[0].grid()
    ax[0].set_ylabel("Years with 1+ Event")

    # Bottom Panel: events
    gdf = df.groupby(ctx["how"]).sum()
    ax[1].bar(xaxis, gdf["count"], width=width)
    ax[1].set_ylabel("Total Event Count")
    ax[1].grid()
    ax[1].set_xlabel(f"Partitioned by {PDICT[ctx['how']]}")
    ax[1].set_xticks(xticks)
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xlim(0, 13 if ctx["how"] == "month" else 366)

    return fig, df


if __name__ == "__main__":
    plotter({"how": "doy"})
