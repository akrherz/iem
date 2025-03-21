"""
This plot presents trailing day precipitation
metrics.  Each point on the x-axis represents a period from that date to
the right-most date on the plot.  There are five options for units to
display the chart in, more specifically, the right hand axis on the
interactive chart version.
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

from datetime import date, datetime, timedelta

import httpx
import numpy as np
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot import ARG_STATION

PDICT = {
    "dep": "Departure [inch]",
    "per": "Percent of Average [%]",
    "ptile": "Percentile (1=wettest)",
    "rank": "Rank (1=wettest)",
    "spi": "Standardized Precip Index [sigma]",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = date.today()
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="opt",
            default="rank",
            options=PDICT,
            label="Interative Chart Variable:",
        ),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="To Date:",
            min="1894/01/01",
        ),
    ]
    return desc


@with_sqlalchemy_conn("coop")
def add_ctx(ctx, conn=None):
    """Get the plotting context"""
    station = ctx["station"]
    dt: date = ctx["date"]
    opt = ctx["opt"]

    res = conn.execute(
        sql_helper("""
    SELECT year, extract(doy from day) as doy, precip from
    alldata where station = :station and precip is not null"""),
        {"station": station},
    )
    if res.rowcount == 0:
        raise NoDataFound("No Data Found")

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    baseyear = ab.year - 1
    ctx["years"] = (datetime.now().year - baseyear) + 1

    data = np.zeros((ctx["years"], 367 * 2))

    for row in res.mappings():
        # left hand
        data[int(row["year"] - baseyear), int(row["doy"])] = row["precip"]
        # right hand
        data[int(row["year"] - baseyear - 1), int(row["doy"]) + 366] = row[
            "precip"
        ]
    sts = dt - timedelta(days=14)
    try:
        resp = httpx.get(
            "http://mesonet.agron.iastate.edu/api/1/usdm_bypoint.json",
            params={
                "sdate": sts.strftime("%Y-%m-%d"),
                "edate": dt.strftime("%Y-%m-%d"),
                "lon": ctx["_nt"].sts[station]["lon"],
                "lat": ctx["_nt"].sts[station]["lat"],
            },
            timeout=30,
        )
        resp.raise_for_status()
    except Exception as exp:
        raise NoDataFound("Unable to fetch USDM data") from exp
    jdata = resp.json()
    dclass = "No Drought"
    if jdata["data"]:
        lastrow = jdata["data"][-1]
        cat = lastrow["category"]
        cat = "No Drought" if cat is None else f"D{cat}"
        ts = datetime.strptime(lastrow["valid"], "%Y-%m-%d")
        dclass = f"{cat} on {ts:%-d %b %Y}"

    _doy = dt.replace(year=2000).timetuple().tm_yday
    xticks = []
    xticklabels = []
    for i in range(-360, 1, 60):
        ts = dt + timedelta(days=i)
        xticks.append(i)
        xticklabels.append(ts.strftime("%b %-d\n'%y"))
    ranks = []
    departures = []
    percentages = []
    totals = []
    maxes = []
    avgs = []
    spi = []
    ptile = []
    myyear = dt.year - baseyear - 1
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

    ctx["sdate"] = dt - timedelta(days=360)
    ctx["title"] = f"[{baseyear + 2}-{datetime.now().year}] {ctx['_sname']}"
    ctx["subtitle"] = (
        f"{PDICT[opt]} from given x-axis date until {dt:%-d %b %Y}, "
        f"US Drought Monitor: {dclass}"
    )
    ctx["subtitle2"] = (
        f"From given x-axis date until {dt:%-d %b %Y}, "
        f"US Drought Monitor: {dclass}"
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


def get_highcharts(ctx: dict) -> str:
    """Go"""
    add_ctx(ctx)
    dstart = "Date.UTC(%s, %s, %s)" % (
        ctx["sdate"].year,
        ctx["sdate"].month - 1,
        ctx["sdate"].day,
    )
    containername = ctx["_e"]
    return (
        """
Highcharts.chart('"""
        + containername
        + """', {
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


def plotter(ctx: dict):
    """Go"""
    add_ctx(ctx)

    fig = figure(title=ctx["title"], subtitle=ctx["subtitle2"], apctx=ctx)
    width = 0.26
    height = 0.38
    x0 = 0.07
    y0 = 0.1
    x1 = x0 + width + 0.06
    y1 = y0 + height + 0.03
    x2 = x1 + width + 0.06
    axes = [
        fig.add_axes((x0, y1, width, height)),
        fig.add_axes((x0, y0, width, height)),
        fig.add_axes((x1, y1, width, height)),
        fig.add_axes((x1, y0, width, height)),
        fig.add_axes((x2, y1, width, height)),
        fig.add_axes((x2, y0, width, height)),
    ]
    for i, ax in enumerate(axes):
        ax.grid(True)
        ax.set_xticks(ctx["xticks"])
        if (i + 1) % 2 == 0:
            ax.set_xticklabels(ctx["xticklabels"])
        else:
            ax.set_xticklabels([])
        ax.set_xlim(-367, 0.5)

    xaxis = np.arange(-365, 0)
    # Upper Left, simple accums
    ax = axes[0]
    ax.plot(
        xaxis,
        ctx["totals"][::-1],
        color="r",
        lw=2,
        label="This Period",
    )
    ax.plot(
        xaxis,
        ctx["avgs"][::-1],
        color="purple",
        lw=2,
        label="Average",
    )
    ax.plot(
        xaxis,
        ctx["maxes"][::-1],
        color="g",
        lw=2,
        label="Maximum",
    )
    ax.set_ylabel("Accum Precipitation [inch]")
    ax.legend(loc=1, ncol=1)
    ax.set_ylim(bottom=0)

    # Lower Left SPI
    ax = axes[1]
    ax.plot(xaxis, ctx["spi"][::-1], zorder=6)
    ax.set_ylabel(r"Standardized Precip Index ($\sigma$)")
    colors = ["#ffff00", "#fcd37f", "#ffaa00", "#e60000", "#730000"]
    for i, spi in enumerate([-0.5, -0.8, -1.3, -1.6, -2]):
        ax.axhline(spi, color=colors[i], lw=2, zorder=4)
        ax.annotate(
            f"D{i}",
            (0.5, spi),
            xycoords=("axes fraction", "data"),
            va="center",
            zorder=5,
            color="k" if i < 3 else "white",
            bbox=dict(color=colors[i]),
        )

    # Middle Upper
    ax = axes[2]
    ax.set_ylabel("Rank (wettest=1)")
    ax.axhline(ctx["years"], color="b", linestyle="-.")
    ax.plot(xaxis, ctx["ranks"][::-1], zorder=6)
    ax.text(-180, ctx["years"] + 2, "Total Years", ha="center")
    ax.set_ylim(1, ctx["years"] + 10)

    # Middle Lower
    ax = axes[3]
    ax.set_ylabel("Percentile (wettest=1)")
    ax.plot(xaxis, ctx["percentiles"][::-1], zorder=6)
    ax.set_ylim(1, 101)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])

    # Upper Right
    ax = axes[4]
    ax.set_ylabel("Percent of Average [%]")
    ax.plot(xaxis, ctx["percentages"][::-1], zorder=6)

    # Lower Right
    ax = axes[5]
    ax.set_ylabel("Departure from Average [inch]")
    ax.plot(xaxis, ctx["departures"][::-1], zorder=6)

    df = pd.DataFrame(
        {
            "day": np.arange(-365, 0),
            "maxaccum": ctx["maxes"][::-1],
            "accum": ctx["totals"][::-1],
            "rank": ctx["ranks"][::-1],
            "spi": ctx["spi"][::-1],
            "percentages": ctx["percentages"][::-1],
            "departures": ctx["departures"][::-1],
        }
    )

    return fig, df
