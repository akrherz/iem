"""Wfo Gantt chart"""
import datetime

import pytz
from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from matplotlib import ticker
from pyiem.nws import vtec
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 600
    desc["data"] = True
    desc[
        "description"
    ] = """
    Gantt chart of watch, warning, and advisories issued
    by an NWS Forecast Office for a start date and number of days of your
    choice. The duration of the individual alert is the maximum found between
    the earliest issuance and latest expiration."""
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        dict(
            type="date",
            name="sdate",
            default="2015/01/01",
            label="Start Date:",
            min="2005/10/01",
        ),  # Comes back to python as yyyy-mm-dd
        dict(
            type="int", name="days", default=10, label="Number of Days in Plot"
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    sts = ctx["sdate"]
    sts = datetime.datetime(sts.year, sts.month, sts.day)
    days = ctx["days"]

    tz = pytz.timezone(ctx["_nt"].sts[station]["tzname"])

    sts = sts.replace(tzinfo=tz)
    ets = sts + datetime.timedelta(days=days)
    df = read_sql(
        """
        SELECT phenomena, significance, eventid,
        min(product_issue at time zone 'UTC') as minproductissue,
        min(issue at time zone 'UTC') as minissue,
        max(expire at time zone 'UTC') as maxexpire,
        max(coalesce(init_expire, expire) at time zone 'UTC') as maxinitexpire,
        extract(year from product_issue) as year
        from warnings
        WHERE wfo = %s and issue > %s and issue < %s
        GROUP by phenomena, significance, eventid, year
        ORDER by minproductissue ASC
    """,
        pgconn,
        params=(station, sts, ets),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No events were found for WFO and time period.")

    events = []
    labels = []
    types = []
    for i, row in df.iterrows():
        endts = max(row[4], row[5]).replace(tzinfo=pytz.utc)
        events.append((row[3].replace(tzinfo=pytz.utc), endts, row[2]))
        labels.append(vtec.get_ps_string(row[0], row[1]))
        types.append("%s.%s" % (row[0], row[1]))

    # If we have lots of WWA, we need to expand vertically a bunch, lets
    # assume we can plot 5 WAA per 100 pixels
    title = "%s-%s NWS %s issued Watch/Warning/Advisories" % (
        sts.strftime("%-d %b %Y"),
        ets.strftime("%-d %b %Y"),
        ctx["_nt"].sts[station]["name"],
    )
    fig = figure(title=title)
    ax = fig.add_axes([0.05, 0.08, 0.73, 0.82])
    if len(events) > 20:
        height = int(len(events) / 6.0) + 1
        fig.set_size_inches(12, height)
        fontsize = 8
    else:
        fontsize = 10

    used = []

    def get_label(i):
        if types[i] in used:
            return ""
        used.append(types[i])
        return "%s (%s)" % (labels[i], types[i])

    halfway = sts + datetime.timedelta(days=days / 2.0)

    for i, e in enumerate(events):
        secs = abs((e[1] - e[0]).days * 86400.0 + (e[1] - e[0]).seconds)
        ax.barh(
            i + 1,
            secs / 86400.0,
            left=e[0],
            align="center",
            fc=vtec.NWS_COLORS.get(types[i], "k"),
            ec=vtec.NWS_COLORS.get(types[i], "k"),
            label=get_label(i),
        )
        align = "left"
        xpos = e[0] + datetime.timedelta(seconds=secs + 3600)
        if xpos > halfway:
            align = "right"
            xpos = e[0] - datetime.timedelta(minutes=90)
        textcolor = vtec.NWS_COLORS.get(
            types[i] if types[i] != "TO.A" else "X", "k"
        )
        ax.text(
            xpos,
            i + 1,
            labels[i].replace("Weather", "Wx") + " " + str(e[2]),
            color=textcolor,
            ha=align,
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0"),
            fontsize=fontsize,
        )

    ax.set_ylabel("Sequential Product Issuance")

    ax.set_ylim(0, len(events) + 1)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1, tz=tz))
    xinterval = int(days / 7) + 1
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=xinterval, tz=tz))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b", tz=tz))

    ax.grid(True)

    ax.set_xlim(sts, ets)

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.0, 1.0),
        fancybox=True,
        shadow=True,
        ncol=1,
        scatterpoints=1,
        fontsize=8,
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict())
