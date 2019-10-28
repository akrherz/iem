"""Period stats"""
from collections import OrderedDict
import datetime

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("avg_high_temp", "Average High Temperature"),
        ("avg_low_temp", "Average Low Temperature"),
        ("avg_temp", "Average Temperature"),
        ("avg_dewp", "Average Dew Point Temp"),
        ("avg_wind_speed", "Average Wind Speed"),
        ("max_high", "Maximum High Temperature"),
        ("min_low", "Minimum Low Temperature"),
        ("precip", "Total Precipitation"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents statistics for a period of
    days each year provided your start date and number of days after that
    date. If your period crosses a year bounds, the plotted year represents
    the year of the start date of the period. <strong>Average Dew Point Temp
    </strong> is computed by averaging the daily max and min dew point values.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="zstation",
            name="station",
            default="DSM",
            label="Select Station",
            network="IA_ASOS",
        ),
        dict(
            type="month",
            name="month",
            default=(today - datetime.timedelta(days=14)).month,
            label="Start Month:",
        ),
        dict(
            type="day",
            name="day",
            default=(today - datetime.timedelta(days=14)).day,
            label="Start Day:",
        ),
        dict(type="int", name="days", default="14", label="Number of Days"),
        dict(
            type="select",
            name="varname",
            default="avg_temp",
            label="Variable to Compute:",
            options=PDICT,
        ),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Year to Highlight in Chart:",
        ),
    ]
    return desc


def nice(val):
    """pretty print"""
    if val == "M":
        return "M"
    if val < 0.01 and val > 0:
        return "Trace"
    return "%.2f" % (val,)


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("iem")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = ctx["days"]
    sts = datetime.date(2012, ctx["month"], ctx["day"])
    ets = sts + datetime.timedelta(days=(days - 1))
    varname = ctx["varname"]
    year = ctx["year"]
    sdays = []
    for i in range(days):
        ts = sts + datetime.timedelta(days=i)
        sdays.append(ts.strftime("%m%d"))

    doff = (days + 1) if ets.year != sts.year else 0
    df = read_sql(
        """
    SELECT extract(year from day - '"""
        + str(doff)
        + """ days'::interval) as yr,
    avg((max_tmpf+min_tmpf)/2.) as avg_temp, avg(max_tmpf) as avg_high_temp,
    avg(min_tmpf) as avg_low_temp,
    sum(pday) as precip, avg(avg_sknt) * 1.15 as avg_wind_speed,
    min(min_tmpf) as min_low,
    max(min_tmpf) as max_low,
    max(max_tmpf) as max_high,
    avg((max_dwpf + min_dwpf)/2.) as avg_dewp
    from summary s JOIN stations t on (s.iemid = t.iemid)
    WHERE t.network = %s and t.id = %s and to_char(day, 'mmdd') in %s
    GROUP by yr ORDER by yr ASC
    """,
        pgconn,
        params=(ctx["network"], station, tuple(sdays)),
    )
    if df.empty:
        raise NoDataFound("No data was found.")

    (fig, ax) = plt.subplots(2, 1, figsize=(8, 6))

    bars = ax[0].bar(
        df["yr"], df[varname], facecolor="r", edgecolor="r", align="center"
    )
    thisvalue = "M"
    for mybar, x, y in zip(bars, df["yr"], df[varname]):
        if x == year:
            mybar.set_facecolor("g")
            mybar.set_edgecolor("g")
            thisvalue = y
    ax[0].set_xlabel("Year, %s = %s" % (year, nice(thisvalue)))
    ax[0].axhline(
        df[varname].mean(), lw=2, label="Avg: %.2f" % (df[varname].mean(),)
    )
    ylabel = r"Temperature $^\circ$F"
    if varname in ["precip"]:
        ylabel = "Precipitation [inch]"
    elif varname in ["avg_wind_speed"]:
        ylabel = "Wind Speed [MPH]"
    ax[0].set_ylabel(ylabel)
    ax[0].set_title(
        ("[%s] %s\n%s from %s through %s")
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            PDICT.get(varname),
            sts.strftime("%d %b"),
            ets.strftime("%d %b"),
        )
    )
    ax[0].grid(True)
    ax[0].legend(ncol=2, fontsize=10)
    ax[0].set_xlim(df["yr"].min() - 1, df["yr"].max() + 1)
    dy = df[varname].max() - df[varname].min()
    ax[0].set_ylim(df[varname].min() - dy * 0.2, df[varname].max() + dy * 0.25)
    box = ax[0].get_position()
    ax[0].set_position([box.x0, box.y0 + 0.02, box.width, box.height * 0.98])

    # Plot 2: CDF
    vals = df[pd.notnull(df[varname])][varname]
    X2 = np.sort(vals)
    ptile = np.percentile(vals, [0, 5, 50, 95, 100])
    N = len(vals)
    F2 = np.array(range(N)) / float(N) * 100.0
    ax[1].plot(X2, 100.0 - F2)
    ax[1].set_xlabel("based on summarized hourly reports, %s" % (ylabel,))
    ax[1].set_ylabel("Observed Frequency [%]")
    ax[1].grid(True)
    ax[1].set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    mysort = df.sort_values(by=varname, ascending=True)
    info = (
        "Min: %.2f %.0f\n95th: %.2f\nMean: %.2f\nSTD: %.2f\n5th: %.2f\n"
        "Max: %.2f %.0f"
    ) % (
        df[varname].min(),
        df["yr"][mysort.index[0]],
        ptile[1],
        df[varname].mean(),
        df[varname].std(),
        ptile[3],
        df[varname].max(),
        df["yr"][mysort.index[-1]],
    )
    ax[1].axvline(thisvalue, lw=2, color="g")
    ax[1].text(
        0.8,
        0.95,
        info,
        transform=ax[1].transAxes,
        va="top",
        bbox=dict(facecolor="white", edgecolor="k"),
    )
    return fig, df


if __name__ == "__main__":
    plotter(dict())
