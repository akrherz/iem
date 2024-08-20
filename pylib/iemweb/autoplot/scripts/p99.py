"""
This plot produces a time series difference
between daily high and low temperatures against climatology. Climatology is
based on the current official NCEI 1991-2020 dataset to compute the daily
average high and low temperature.  The period of record data is used to compute
the daily standard deviation departures.
"""

import datetime

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION

PDICT = {"abs": "Departure in degrees", "sigma": "Depature in sigma"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="year",
            name="year",
            default=datetime.date.today().year,
            label="Which Year:",
        ),
        dict(
            type="select",
            name="delta",
            options=PDICT,
            label="How to present the daily departures",
            default="abs",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    delta = ctx["delta"]
    year = ctx["year"]
    clstation = ctx["_nt"].sts[station]["ncei91"]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text("""
            WITH days as (
                select generate_series(:sts, :ets,
                    '1 day'::interval)::date as day,
                    to_char(generate_series(:sts, :ets,
                    '1 day'::interval)::date, 'mmdd') as sday
            ),
            official as (
                select to_char(valid, 'mmdd') as sday, high as avg_high,
                low as avg_low from
                ncei_climate91 where station = :clstation
            ),
            climo as (
                SELECT sday, stddev(high) as stddev_high,
                stddev(low) as stddev_low from alldata
                WHERE station = :station GROUP by sday
            ),
            thisyear as (
                SELECT day, sday, high, low from alldata
                WHERE station = :station and year = :year
            ),
            thisyear2 as (
                SELECT d.day, d.sday, t.high, t.low from days d LEFT JOIN
                thisyear t on (d.sday = t.sday)
            )
            SELECT t.day, t.sday, t.high, t.low, o.avg_high, o.avg_low,
            c.stddev_high, c.stddev_low from thisyear2 t, climo c, official o
            WHERE c.sday = t.sday and t.sday = o.sday ORDER by t.day ASC
        """),
            conn,
            params={
                "clstation": clstation,
                "sts": datetime.date(year, 1, 1),
                "ets": datetime.date(year, 12, 31),
                "station": station,
                "year": year,
            },
            index_col="day",
        )
    if df.empty or df["stddev_high"].min() == 0:
        raise NoDataFound("No Data Found.")
    df.index.name = "Date"
    df["high_sigma"] = (df["high"] - df["avg_high"]) / df["stddev_high"]
    df["low_sigma"] = (df["low"] - df["avg_low"]) / df["stddev_low"]

    title = f"{ctx['_sname']} :: Climatology & {year} Observations"
    fig = figure(
        apctx=ctx,
        title=title,
        subtitle=f"NCEI 1991-2020 Climatology Source: {clstation}",
    )
    ax = fig.subplots(2, 1, sharex=True)

    ax[0].plot(
        df.index.values,
        df["avg_high"].values,
        color="r",
        linestyle="-",
        label="Climate High",
    )
    ax[0].plot(
        df.index.values, df["avg_low"].values, color="b", label="Climate Low"
    )
    ax[0].set_ylabel(r"Temperature $^\circ\mathrm{F}$")

    ax[0].plot(
        df.index.values,
        df["high"].values,
        color="brown",
        label=f"{year} High",
    )
    ax[0].plot(
        df.index.values,
        df["low"].values,
        color="green",
        label=f"{year} Low",
    )

    if delta == "abs":
        ax[1].plot(
            df.index.values,
            (df.high - df.avg_high).values,
            color="r",
            label=f"High Diff {year} - Climate",
        )
        ax[1].plot(
            df.index.values,
            (df.low - df.avg_low).values,
            color="b",
            label="Low Diff",
        )
        ax[1].set_ylabel(r"Temp Difference $^\circ\mathrm{F}$")
    else:
        ax[1].plot(
            df.index.values,
            df.high_sigma.values,
            color="r",
            label=f"High Diff {year} - Climate",
        )
        ax[1].plot(
            df.index.values, df.low_sigma.values, color="b", label="Low Diff"
        )
        ax[1].set_ylabel(r"Temp Difference $\sigma$")
        ymax = max([df.high_sigma.abs().max(), df.low_sigma.abs().max()]) + 1
        ax[1].set_ylim(0 - ymax, ymax)
    ax[1].legend(fontsize=10, ncol=2, loc="best")
    ax[1].grid(True)

    ax[0].legend(fontsize=10, ncol=2, loc=8)
    ax[0].grid()
    ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    ax[0].set_xlim(
        df.index.min() - datetime.timedelta(days=3),
        df.index.max() + datetime.timedelta(days=3),
    )

    return fig, df
