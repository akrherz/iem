"""first and last date stuff"""
import datetime
import calendar

import numpy as np
from pyiem import network
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pandas.io.sql import read_sql
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """For each year, the average first and last date of
    a given temperature is computed.  The values are then averaged and plotted
    to represent the period between these occurences and also the number of
    days represented by the period.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        )
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))
    today = datetime.datetime.now()
    thisyear = today.year

    df = read_sql(
        """
    with data as (
        select year, month, extract(doy from day) as doy,
        generate_series(32, high) as t from """
        + table
        + """
        where station = %s and year < %s),
    agger as (
        SELECT year, t, min(doy), max(doy) from data GROUP by year, t)

    SELECT t as tmpf, avg(min) as min_jday,
    avg(max) as max_jday from agger GROUP by t ORDER by t ASC
    """,
        pgconn,
        params=(station, thisyear),
        index_col="tmpf",
    )
    if df.empty:
        raise NoDataFound("No Data Found.")

    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes([0.1, 0.1, 0.7, 0.8])
    ax2 = plt.axes([0.81, 0.1, 0.15, 0.8])
    height = df["min_jday"][:] + 365.0 - df["max_jday"]
    ax2.plot(height, df.index.values)
    ax2.set_xticks([30, 90, 180, 365])
    plt.setp(ax2.get_yticklabels(), visible=False)
    ax2.set_ylim(32, df.index.values.max() + 5)
    ax2.grid(True)
    ax2.text(
        0.96,
        0.02,
        "Days",
        transform=ax2.transAxes,
        bbox=dict(color="white"),
        ha="right",
    )
    ax.text(
        0.96,
        0.02,
        "Period",
        transform=ax.transAxes,
        bbox=dict(color="white"),
        ha="right",
    )
    ax.set_ylim(32, df.index.values.max() + 5)

    ax.barh(
        df.index.values - 0.5,
        height,
        left=df["max_jday"].values,
        ec="tan",
        fc="tan",
        height=1.1,
    )
    days = np.array([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    days = np.concatenate([days, days + 365])
    ax.set_xticks(days)
    months = calendar.month_abbr[1:] + calendar.month_abbr[1:]
    ax.set_xticklabels(months)

    ax.set_ylabel("High Temperature $^\circ$F")
    ax.set_xlim(min(df["max_jday"]) - 1, max(df["max_jday"] + height) + 1)
    ax.grid(True)

    msg = (
        "[%s] %s Period Between Average Last and "
        "First High Temperature of Year"
    ) % (station, nt.sts[station]["name"])
    tokens = msg.split()
    sz = int(len(tokens) / 2)
    ax.set_title(" ".join(tokens[:sz]) + "\n" + " ".join(tokens[sz:]))

    return fig, df


if __name__ == "__main__":
    plotter(dict())
