"""
This plot presents the trailing X number of days
temperature or precipitation departure from long term average. You can
express this departure either in Absolute Departure or as a Standard
Deviation.  The Standard Deviation option along with precipitation is
typically called the "Standardized Precipitation Index".

<p>The plot also contains an underlay with the weekly US Drought Monitor
that is valid for the station location.  If you plot a climate district
station, you get the US Drought Monitor valid for the district centroid.
If you plot a statewide average, you get no USDM included.
"""

import datetime
import sys

import matplotlib.dates as mdates
import pandas as pd
import requests
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context

UNITS = {"precip": "inch", "avgt": "F", "high": "F", "low": "F"}
PDICT = {
    "precip": "Precipitation",
    "avgt": "Daily Average Temperature",
    "high": "Daily High Temperature",
    "low": "Daily Low Temperature",
}
PDICT2 = {"diff": "Absolute Departure", "sigma": "Standard Deviation"}
COLORS = ["#ffff00", "#fcd37f", "#ffaa00", "#e60000", "#730000"]


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    today = datetime.date.today()
    sts = today - datetime.timedelta(days=720)
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(type="int", name="p1", default=31, label="First Period of Days"),
        dict(type="int", name="p2", default=91, label="Second Period of Days"),
        dict(type="int", name="p3", default=365, label="Third Period of Days"),
        dict(
            type="date",
            name="sdate",
            default=sts.strftime("%Y/%m/%d"),
            min="1893/01/01",
            label="Start Date of Plot",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            min="1893/01/01",
            label="End Date of Plot",
        ),
        dict(
            type="select",
            name="pvar",
            default="precip",
            options=PDICT,
            label="Which variable to plot?",
        ),
        dict(
            type="select",
            name="how",
            default="diff",
            options=PDICT2,
            label="How to Express Departure?",
        ),
    ]
    return desc


def underlay_usdm(axis, sts, ets, lon, lat):
    """Underlay the USDM as pretty bars, somehow"""
    if ets < datetime.date(2000, 1, 1):
        axis.text(
            0.0,
            1.03,
            "No Drought Information Prior to 2000",
            transform=axis.transAxes,
        )
        return
    rects = [Rectangle((0, 0), 1, 1, fc=color) for color in COLORS]
    axis.text(
        0.0, 1.03, "Drought Category Underlain", transform=axis.transAxes
    )
    legend = plt.legend(
        rects,
        [f"D{cat}" for cat in range(5)],
        ncol=5,
        fontsize=11,
        loc=(0.3, 1.01),
    )
    axis.add_artist(legend)
    uri = (
        "http://mesonet.agron.iastate.edu/"
        "api/1/usdm_bypoint.json?sdate=%s&edate=%s&lon=%s&lat=%s"
    ) % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d"), lon, lat)
    data = requests.get(uri, timeout=30).json()
    if not data["data"]:
        return
    for row in data["data"]:
        if row["category"] is None:
            continue
        ts = datetime.datetime.strptime(row["valid"], "%Y-%m-%d")
        date = datetime.date(ts.year, ts.month, ts.day)
        axis.axvspan(
            date,
            date + datetime.timedelta(days=7),
            color=COLORS[row["category"]],
            zorder=-3,
        )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    p1 = ctx["p1"]
    p2 = ctx["p2"]
    p3 = ctx["p3"]
    pvar = ctx["pvar"]
    sts = ctx["sdate"]
    ets = ctx["edate"]
    how = ctx["how"]
    maxdays = max([p1, p2, p3])

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
        -- Get all period averages
        with avgs as (
            SELECT day, sday,
            count(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as counts,
            avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as p1_high,
            avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as p2_high,
            avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as p3_high,
            avg(low) OVER (ORDER by day ASC ROWS %s PRECEDING) as p1_low,
            avg(low) OVER (ORDER by day ASC ROWS %s PRECEDING) as p2_low,
            avg(low) OVER (ORDER by day ASC ROWS %s PRECEDING) as p3_low,
            avg((high+low)/2.)
                OVER (ORDER by day ASC ROWS %s PRECEDING) as p1_avgt,
            avg((high+low)/2.)
                OVER (ORDER by day ASC ROWS %s PRECEDING) as p2_avgt,
            avg((high+low)/2.)
                OVER (ORDER by day ASC ROWS %s PRECEDING) as p3_avgt,
            sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as p1_precip,
            sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as p2_precip,
            sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as p3_precip
            from alldata WHERE station = %s
        ),
        -- Get sday composites
        sdays as (
            SELECT sday,
            avg(p1_high) as p1_high_avg, stddev(p1_high) as p1_high_stddev,
            avg(p2_high) as p2_high_avg, stddev(p2_high) as p2_high_stddev,
            avg(p3_high) as p3_high_avg, stddev(p3_high) as p3_high_stddev,
            avg(p1_low) as p1_low_avg, stddev(p1_low) as p1_low_stddev,
            avg(p2_low) as p2_low_avg, stddev(p2_low) as p2_low_stddev,
            avg(p3_low) as p3_low_avg, stddev(p3_low) as p3_low_stddev,
            avg(p1_avgt) as p1_avgt_avg, stddev(p1_avgt) as p1_avgt_stddev,
            avg(p2_avgt) as p2_avgt_avg, stddev(p2_avgt) as p2_avgt_stddev,
            avg(p3_avgt) as p3_avgt_avg, stddev(p3_avgt) as p3_avgt_stddev,
            avg(p1_precip) as p1_precip_avg,
            stddev(p1_precip) as p1_precip_stddev,
            avg(p2_precip) as p2_precip_avg,
            stddev(p2_precip) as p2_precip_stddev,
            avg(p3_precip) as p3_precip_avg,
            stddev(p3_precip) as p3_precip_stddev
            from avgs WHERE counts = %s GROUP by sday
        )
        -- Now merge to get obs
            SELECT day, s.sday,
            p1_high - p1_high_avg as p1_high_diff,
            p2_high - p2_high_avg as p2_high_diff,
            p3_high - p3_high_avg as p3_high_diff,
            p1_low - p1_low_avg as p1_low_diff,
            p2_low - p2_low_avg as p2_low_diff,
            p3_low - p3_low_avg as p3_low_diff,
            p1_avgt - p1_avgt_avg as p1_avgt_diff,
            p2_avgt - p2_avgt_avg as p2_avgt_diff,
            p3_avgt - p3_avgt_avg as p3_avgt_diff,
            p1_precip - p1_precip_avg as p1_precip_diff,
            p2_precip - p2_precip_avg as p2_precip_diff,
            p3_precip - p3_precip_avg as p3_precip_diff,
            (p1_high - p1_high_avg) / p1_high_stddev as p1_high_sigma,
            (p2_high - p2_high_avg) / p2_high_stddev as p2_high_sigma,
            (p3_high - p3_high_avg) / p3_high_stddev as p3_high_sigma,
            (p1_low - p1_low_avg) / p1_low_stddev as p1_low_sigma,
            (p2_low - p2_low_avg) / p2_low_stddev as p2_low_sigma,
            (p3_low - p3_low_avg) / p3_low_stddev as p3_low_sigma,
            (p1_avgt - p1_avgt_avg) / p1_avgt_stddev as p1_avgt_sigma,
            (p2_avgt - p2_avgt_avg) / p2_avgt_stddev as p2_avgt_sigma,
            (p3_avgt - p3_avgt_avg) / p3_avgt_stddev as p3_avgt_sigma,
            (p1_precip - p1_precip_avg) / p1_precip_stddev as p1_precip_sigma,
            (p2_precip - p2_precip_avg) / p2_precip_stddev as p2_precip_sigma,
            (p3_precip - p3_precip_avg) / p3_precip_stddev as p3_precip_sigma
            from avgs a JOIN sdays s on (a.sday = s.sday) WHERE
            day >= %s and day <= %s ORDER by day ASC
        """,
            conn,
            params=(
                maxdays - 1,
                p1 - 1,
                p2 - 1,
                p3 - 1,
                p1 - 1,
                p2 - 1,
                p3 - 1,
                p1 - 1,
                p2 - 1,
                p3 - 1,
                p1 - 1,
                p2 - 1,
                p3 - 1,
                station,
                maxdays,
                sts,
                ets,
            ),
            index_col="day",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    (fig, ax) = figure_axes(apctx=ctx)
    ax.set_position([0.1, 0.14, 0.85, 0.71])

    (l1,) = ax.plot(
        df.index.values,
        df["p1_" + pvar + "_" + how],
        lw=2,
        label="%s Day" % (p1,),
        zorder=5,
    )
    (l2,) = ax.plot(
        df.index.values,
        df["p2_" + pvar + "_" + how],
        lw=2,
        label="%s Day" % (p2,),
        zorder=5,
    )
    (l3,) = ax.plot(
        df.index.values,
        df["p3_" + pvar + "_" + how],
        lw=2,
        label="%s Day" % (p3,),
        zorder=5,
    )
    fig.text(
        0.5,
        0.93,
        f"{ctx['_sname']}\n"
        f"Trailing {p1}, {p2}, {p3} Day Departures & "
        "US Drought Monitor",
        ha="center",
        fontsize=14,
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.set_ylabel(
        ("%s [%s] %s")
        % (
            PDICT.get(pvar),
            UNITS[pvar] if how == "diff" else r"$\sigma$",
            PDICT2[how],
        )
    )
    ax.grid(True)
    legend = plt.legend(handles=[l1, l2, l3], ncol=3, fontsize=12, loc="best")
    ax.add_artist(legend)
    ax.text(
        1,
        -0.14,
        "%s to %s" % (sts.strftime("%-d %b %Y"), ets.strftime("%-d %b %Y")),
        va="bottom",
        ha="right",
        fontsize=12,
        transform=ax.transAxes,
    )
    if station[2:] != "0000":
        try:
            underlay_usdm(
                ax,
                sts,
                ets,
                ctx["_nt"].sts[station]["lon"],
                ctx["_nt"].sts[station]["lat"],
            )
        except Exception as exp:
            sys.stderr.write(str(exp))
    offset = datetime.timedelta(days=2)
    ax.set_xlim(df.index.min() - offset, df.index.max() + offset)

    return fig, df
