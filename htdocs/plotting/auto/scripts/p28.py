"""trailing day precip."""
import datetime
from collections import OrderedDict

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("dep", "Departure [inch]"),
        ("per", "Percent of Average [%]"),
        ("ptile", "Percentile (1=wettest)"),
        ("rank", "Rank (1=wettest)"),
        ("spi", "Standardized Precip Index [sigma]"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    today = datetime.date.today()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents trailing day precipitation
    metrics.  Each point on the x-axis represents a period from that date to
    the right-most date on the plot.  There are five options for units to
    display the chart in, more specifically, the right hand axis.
    <br />
    <ul>
      <li><strong>Departure [inch]</strong>: the absolute amount of precip
      above or below long term average.</li>
      <li><strong>Percent of Average [%]</strong>: the departure from average
      expressed in percent of average.</li>
      <li><strong>Percentile (1=wettest)</strong>: The percentile rank for
      this period's total versus all totals from the same period of days
      over the period of record for the station.</li>
      <li><strong>Rank (1=wettest)</strong>: The overall rank over the other
      years for the period of record for the location.</li>
      <li><strong>Standardized Precip Index [sigma]</strong>: This expresses
      the precipitation departure in terms of standard deviations from
      average.  The standard deviations and averages are based on period of
      record data.</li>
    </ul>
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="opt",
            default="rank",
            options=PDICT,
            label="Chart Display Units",
        ),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="To Date:",
            min="1894/01/01",
        ),  # Comes back to python as yyyy-mm-dd
    ]
    return desc


def get_ctx(fdict):
    """Get the plotting context """
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    date = ctx["date"]
    opt = ctx["opt"]

    table = "alldata_%s" % (station[:2],)

    cursor.execute(
        f"""
        SELECT year,  extract(doy from day) as doy, precip
        from {table} where station = %s and precip is not null
    """,
        (station,),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found")

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    baseyear = ab.year - 1
    ctx["years"] = (datetime.datetime.now().year - baseyear) + 1

    data = np.zeros((ctx["years"], 367 * 2))
    # 1892 1893
    # 1893 1894
    # 1894 1895

    for row in cursor:
        # left hand
        data[int(row["year"] - baseyear), int(row["doy"])] = row["precip"]
        # right hand
        data[int(row["year"] - baseyear - 1), int(row["doy"]) + 366] = row[
            "precip"
        ]

    _temp = date.replace(year=2000)
    _doy = int(_temp.strftime("%j"))
    xticks = []
    xticklabels = []
    for i in range(-366, 0):
        ts = _temp + datetime.timedelta(days=i)
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%b"))
    ranks = []
    departures = []
    percentages = []
    totals = []
    maxes = []
    avgs = []
    spi = []
    ptile = []
    myyear = date.year - baseyear - 1
    for days in range(1, 366):
        idx0 = _doy + 366 - days
        idx1 = _doy + 366
        sums = np.sum(data[:, idx0:idx1], 1)
        thisyear = sums[myyear]
        sums = np.sort(sums)
        arr = np.digitize([thisyear], sums)
        if thisyear == 0:
            rank = ctx["years"]
        else:
            rank = ctx["years"] - arr[0] + 1
        ranks.append(rank)
        ptile.append(rank / float(len(sums)) * 100.0)
        totals.append(thisyear)
        maxes.append(sums[-1])
        avgs.append(np.nanmean(sums))
        departures.append(thisyear - avgs[-1])
        percentages.append(thisyear / avgs[-1] * 100)
        spi.append((thisyear - avgs[-1]) / np.nanstd(sums))

    ctx["sdate"] = date - datetime.timedelta(days=360)
    ctx["title"] = "%s %s" % (station, ctx["_nt"].sts[station]["name"])
    ctx["subtitle"] = ("Trailing Days Precip %s [%s-%s] to %s") % (
        PDICT[opt],
        baseyear + 2,
        datetime.datetime.now().year,
        date.strftime("%-d %b %Y"),
    )

    ctx["ranks"] = ranks
    ctx["departures"] = departures
    ctx["percentages"] = percentages
    ctx["spi"] = spi
    ctx["percentiles"] = ptile
    if opt == "per":
        ctx["y2"] = ctx["percentages"]
    elif opt == "dep":
        ctx["y2"] = ctx["departures"]
    elif opt == "spi":
        ctx["y2"] = ctx["spi"]
    elif opt == "ptile":
        ctx["y2"] = ctx["percentiles"]
    else:
        ctx["y2"] = ctx["ranks"]
    ctx["totals"] = totals
    ctx["maxes"] = maxes
    ctx["avgs"] = avgs
    ctx["xticks"] = xticks
    ctx["xticklabels"] = xticklabels
    ctx["station"] = station
    ctx["y2label"] = PDICT[opt]
    return ctx


def highcharts(fdict):
    """ Go """
    ctx = get_ctx(fdict)
    dstart = "Date.UTC(%s, %s, %s)" % (
        ctx["sdate"].year,
        ctx["sdate"].month - 1,
        ctx["sdate"].day,
    )
    return (
        """
$("#ap_container").highcharts({
    time: {useUTC: false},
    title: {text: '"""
        + ctx["title"]
        + """'},
    subtitle: {text: '"""
        + ctx["subtitle"]
        + """'},
    chart: {zoomType: 'x'},
    yAxis: [{
            min: 0,
            title: {
                text: 'Precipitation [inch]'
            }
        }, {
            title: {
                text: '"""
        + ctx["y2label"]
        + """',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            labels: {
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            opposite: true
    }],
    tooltip: {
        shared: true,
        xDateFormat: '%Y-%m-%d'
    },
    series : [{
        name: '"""
        + ctx["y2label"]
        + """ (right axis)',
        tooltip: {valueDecimals: 2},
        pointStart: """
        + dstart
        + """,
        pointInterval: 24 * 3600 * 1000, // one day
        zIndex: 5,
        shadow: true,
        data: """
        + str(ctx["y2"][::-1])
        + """,
        yAxis: 1
    },{
        name: 'This Period',
        tooltip: {valueDecimals: 2},
        pointStart: """
        + dstart
        + """,
        pointInterval: 24 * 3600 * 1000, // one day
        zIndex: 3,
        data: """
        + str(ctx["totals"][::-1])
        + """
    },{
        name: 'Average',
        tooltip: {valueDecimals: 2},
        pointStart: """
        + dstart
        + """,
        pointInterval: 24 * 3600 * 1000, // one day
        zIndex: 4,
        data: """
        + str(ctx["avgs"][::-1])
        + """
    }, {
        name: 'Maximum',
        zIndex: 2,
        tooltip: {valueDecimals: 2},
        pointStart: """
        + dstart
        + """,
        pointInterval: 24 * 3600 * 1000, // one day
        data: """
        + str(ctx["maxes"][::-1])
        + """
    }],
    xAxis: {
        type: 'datetime'
    }

});

    """
    )


def plotter(fdict):
    """ Go """
    ctx = get_ctx(fdict)

    (fig, ax) = plt.subplots(1, 1)
    ax.set_position([0.1, 0.1, 0.75, 0.75])
    y2 = ax.twinx()
    y2.set_position([0.1, 0.1, 0.75, 0.75])

    y2.plot(np.arange(-365, 0), ctx["y2"][::-1], color="b", lw=2)
    if ctx["opt"] == "rank":
        y2.axhline(ctx["years"], color="b", linestyle="-.")
        y2.text(-180, ctx["years"] + 2, "Total Years", ha="center")
        y2.set_ylim(0, ctx["years"] + 30)
    ax.grid(True)
    ax.set_xticks(ctx["xticks"])
    ax.set_xticklabels(ctx["xticklabels"])
    ax.set_title(("%s\n%s") % (ctx["title"], ctx["subtitle"]), fontsize=10)
    y2.set_ylabel("%s (blue line)" % (ctx["y2label"],), color="b")
    ax.set_xlim(-367, 0.5)

    ax.plot(
        np.arange(-365, 0),
        ctx["totals"][::-1],
        color="r",
        lw=2,
        label="This Period",
    )
    ax.plot(
        np.arange(-365, 0),
        ctx["avgs"][::-1],
        color="purple",
        lw=2,
        label="Average",
    )
    ax.plot(
        np.arange(-365, 0),
        ctx["maxes"][::-1],
        color="g",
        lw=2,
        label="Maximum",
    )
    ax.set_ylabel("Precipitation [inch]")
    ax.set_zorder(y2.get_zorder() + 1)
    ax.patch.set_visible(False)
    ax.legend(loc="best", ncol=3)
    ax.set_ylim(bottom=0)
    df = pd.DataFrame(
        dict(
            day=np.arange(-365, 0),
            maxaccum=ctx["maxes"][::-1],
            accum=ctx["totals"][::-1],
            rank=ctx["ranks"][::-1],
            spi=ctx["spi"][::-1],
            percentages=ctx["percentages"][::-1],
            departures=ctx["departures"][::-1],
        )
    )

    return fig, df


if __name__ == "__main__":
    highcharts(dict())
