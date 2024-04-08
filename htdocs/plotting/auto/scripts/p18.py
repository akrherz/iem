"""
This chart displays a simple time series of
an observed variable for a location of your choice.  For sites in the
US, the daily high and low temperature climatology is presented as a
filled bar for each day plotted when Air Temperature is selected.
"""

import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

MDICT = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temperature",
    "feel": "Feels Like Temperature",
    "alti": "Pressure Altimeter",
    "relh": "Relative Humidity",
    "mslp": "Sea Level Pressure",
}
UNITS = {
    "tmpf": "°F",
    "dwpf": "°F",
    "alti": "inch",
    "mslp": "mb",
    "feel": "°F",
    "relh": "%",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    ts = datetime.date.today() - datetime.timedelta(days=365)
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="date",
            name="sdate",
            default=ts.strftime("%Y/%m/%d"),
            label="Start Date of Plot:",
            min="1951/01/01",
        ),  # Comes back to python as yyyy-mm-dd
        dict(type="int", name="days", default="365", label="Days to Plot"),
        dict(
            type="select",
            name="var",
            options=MDICT,
            default="tmpf",
            label="Variable to Plot",
        ),
    ]
    return desc


def highcharts(fdict):
    """Highcharts output"""
    ctx = get_data(fdict)
    ranges = []
    now = ctx["sdate"]
    oneday = datetime.timedelta(days=1)
    while ctx["climo"] and (now - oneday) <= ctx["edate"]:
        ranges.append(
            [
                int(now.strftime("%s")) * 1000.0,
                ctx["climo"][now.strftime("%m%d")]["low"],
                ctx["climo"][now.strftime("%m%d")]["high"],
            ]
        )
        now += oneday

    j = {}
    j["title"] = dict(text=f"{ctx['_sname']} Time Series")
    j["xAxis"] = dict(type="datetime")
    j["yAxis"] = dict(
        title=dict(text="%s %s" % (MDICT[ctx["var"]], UNITS[ctx["var"]]))
    )
    j["tooltip"] = {
        "crosshairs": True,
        "shared": True,
        "valueSuffix": " %s" % (UNITS[ctx["var"]],),
    }
    j["legend"] = {}
    j["time"] = {"useUTC": False}
    j["exporting"] = {"enabled": True}
    j["chart"] = {"zoomType": "x"}
    j["plotOptions"] = {"line": {"turboThreshold": 0}}
    j["series"] = [
        {
            "name": MDICT[ctx["var"]],
            "data": list(
                zip(
                    ctx["df"].ticks.values.tolist(),
                    ctx["df"].datum.values.tolist(),
                )
            ),
            "zIndex": 2,
            "color": "#FF0000",
            "lineWidth": 2,
            "marker": {"enabled": False},
            "type": "line",
        }
    ]
    if ranges:
        j["series"].append(
            {
                "name": "Climo Hi/Lo Range",
                "data": ranges,
                "type": "arearange",
                "lineWidth": 0,
                "color": "#ADD8E6",
                "fillOpacity": 0.3,
                "zIndex": 0,
            }
        )
    if ctx["var"] in ["tmpf", "dwpf"]:
        j["yAxis"]["plotLines"] = [
            {
                "value": 32,
                "width": 2,
                "zIndex": 1,
                "color": "#000",
                "label": {"text": "32°F"},
            }
        ]

    return j


def get_data(fdict):
    """Get data common to both methods"""
    ctx = get_autoplot_context(fdict, get_description())
    coop_pgconn, ccursor = get_dbconnc("coop")
    ctx["station"] = ctx["zstation"]
    sdate = ctx["sdate"]
    days = ctx["days"]
    ctx["edate"] = sdate + datetime.timedelta(days=days)
    today = datetime.date.today()
    if ctx["edate"] > today:
        ctx["edate"] = today
        ctx["days"] = (ctx["edate"] - sdate).days

    ctx["climo"] = None
    if ctx["var"] == "tmpf":
        ctx["climo"] = {}
        ccursor.execute(
            "SELECT valid, high, low from ncei_climate91 where station = %s",
            (ctx["_nt"].sts[ctx["station"]]["ncei91"],),
        )
        for row in ccursor:
            ctx["climo"][row["valid"].strftime("%m%d")] = dict(
                high=row["high"], low=row["low"]
            )
    col = "tmpf::int" if ctx["var"] == "tmpf" else ctx["var"]
    col = "dwpf::int" if ctx["var"] == "dwpf" else col
    with get_sqlalchemy_conn("asos") as conn:
        ctx["df"] = pd.read_sql(
            "SELECT valid at time zone 'UTC' as valid, "
            f"extract(epoch from valid) * 1000 as ticks, {col} as datum "
            "from alldata WHERE station = %s and valid > %s and valid < %s "
            f"and {ctx['var']} is not null and report_type != 1 "
            "ORDER by valid ASC",
            conn,
            params=(
                ctx["station"],
                sdate,
                sdate + datetime.timedelta(days=days),
            ),
            index_col="valid",
        )
    coop_pgconn.close()
    if ctx["df"].empty:
        raise NoDataFound("No data found.")

    return ctx


def plotter(fdict):
    """Go"""
    ctx = get_data(fdict)
    title = (
        f"{ctx['_sname']}\n"
        f"{MDICT[ctx['var']]} Timeseries {ctx['sdate']:%d %b %Y} - "
        f"{ctx['edate']:%d %b %Y}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    xticks = []
    xticklabels = []
    now = ctx["sdate"]
    cdates = []
    chighs = []
    clows = []
    oneday = datetime.timedelta(days=1)
    while ctx["climo"] is not None and (now - oneday) <= ctx["edate"]:
        cdates.append(now)
        chighs.append(ctx["climo"][now.strftime("%m%d")]["high"])
        clows.append(ctx["climo"][now.strftime("%m%d")]["low"])
        if now.day == 1 or (now.day % 12 == 0 and ctx["days"] < 180):
            xticks.append(now)
            fmt = "%-d"
            if now.day == 1:
                fmt = "%-d\n%b"
            xticklabels.append(now.strftime(fmt))

        now += oneday
    while (now - oneday) <= ctx["edate"]:
        if now.day == 1 or (now.day % 12 == 0 and ctx["days"] < 180):
            xticks.append(now)
            fmt = "%-d"
            if now.day == 1:
                fmt = "%-d\n%b"
            xticklabels.append(now.strftime(fmt))
        now += oneday

    if chighs:
        chighs = np.array(chighs)
        clows = np.array(clows)
        ax.bar(
            cdates,
            chighs - clows,
            bottom=clows,
            width=1,
            align="edge",
            fc="lightblue",
            ec="lightblue",
            label="Daily Climatology",
        )
    # Construct a local timezone x axis
    x = (
        ctx["df"]
        .index.tz_localize(ZoneInfo("UTC"))
        .tz_convert(ctx["_nt"].sts[ctx["station"]]["tzname"])
        .tz_localize(None)
    )
    ax.plot(x.values, ctx["df"]["datum"], color="r", label="Hourly Obs")
    ax.set_ylabel("%s %s" % (MDICT[ctx["var"]], UNITS[ctx["var"]]))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(ctx["sdate"], ctx["edate"] + oneday)
    ax.set_ylim(top=ctx["df"].datum.max() + 15.0)
    ax.legend(loc=2, ncol=2)
    ax.axhline(32, linestyle="-.")
    ax.grid(True)
    return fig, ctx["df"]


if __name__ == "__main__":
    highcharts({})
