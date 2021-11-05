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


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart shows the weekly frequency of having
    at least one watch/warning/advisory (WWA) issued by the Weather Forecast
    Office (top plot) and the overall number of WWA issued for
    that week of the year (bottom plot).  For example, if 10 Tornado Warnings
    were issued during the 30th week of 2014, this would count as 1 year in
    the top plot and 10 events in the bottom plot.  This plot hopefully
    answers the question of which week of the year is most common to get a
    certain WWA type and which week has seen the most WWAs issued.  The plot
    only considers issuance date. When plotting for a state, an event is
    defined on a per forecast office basis."""
    desc["arguments"] = [
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

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    fig = figure(apctx=ctx)
    ax = fig.subplots(2, 1, sharex=True)

    limiter = " wfo = '%s' " % (station,)
    title = "[%s] NWS %s" % (station, ctx["_nt"].sts[station]["name"])
    if opt == "state":
        title = "State of %s" % (reference.state_names[state],)
        limiter = " substr(ugc, 1, 2) = '%s' " % (state,)
    df = read_sql(
        f"""
    with obs as (
        SELECT distinct extract(year from issue) as yr,
        extract(week from issue) as week, wfo, eventid from warnings WHERE
        {limiter} and phenomena = %s and significance = %s
    )
    SELECT yr, week, count(*) from obs GROUP by yr, week ORDER by yr ASC
    """,
        pgconn,
        params=(phenomena, significance),
        index_col=None,
    )

    if df.empty:
        raise NoDataFound("ERROR: No Results Found!")

    # Top Panel: count
    gdf = df.groupby("week").count()
    ax[0].bar((gdf.index.values - 1) * 7, gdf["yr"], width=7)
    ax[0].set_title(
        ("%s\n%s (%s.%s) Events - %i to %i")
        % (
            title,
            vtec.get_ps_string(phenomena, significance),
            phenomena,
            significance,
            df["yr"].min(),
            df["yr"].max(),
        )
    )
    ax[0].grid()
    ax[0].set_ylabel("Years with 1+ Event")

    # Bottom Panel: events
    gdf = df.groupby("week").sum()
    ax[1].bar((gdf.index.values - 1) * 7, gdf["count"], width=7)
    ax[1].set_ylabel("Total Event Count")
    ax[1].grid()
    ax[1].set_xlabel("Partitioned by Week of the Year")
    ax[1].set_xticks(xticks)
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xlim(0, 366)

    return fig, df


if __name__ == "__main__":
    plotter(dict())
