"""
This plot presents a time series of Aridity Index.
This index computes the standardized high temperature departure subtracted
by the standardized precipitation departure.  For the purposes of this
plot, this index is computed daily over a trailing period of days of your
choice.  The climatology is based on the present period of record
statistics.  You can optionally plot this index for two other period of
days of your choice.  Entering '0' will disable additional lines appearing
on the plot.

<br />You can also optionally generate this plot for the same period of
days over different years of your choice.  When plotted over multiple
years, only "Number of Days #1' is considered.  An additional year is
plotted representing the best root mean squared error fit to the selected
year's data.
"""

from datetime import date, timedelta

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest, NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

from iemweb.autoplot import ARG_STATION


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    today = date.today()
    sts = today - timedelta(days=180)
    desc["arguments"] = [
        ARG_STATION,
        dict(type="int", name="days", default=91, label="Number of Days #1"),
        dict(
            type="int",
            name="days2",
            default=0,
            label="Number of Days #2 (0 disables)",
        ),
        dict(
            type="int",
            name="days3",
            default=0,
            label="Number of Days #3 (0 disables)",
        ),
        dict(
            type="year",
            name="year2",
            default=2004,
            optional=True,
            label="Compare with year (optional):",
        ),
        dict(
            type="year",
            name="year3",
            default=2012,
            optional=True,
            label="Compare with year (optional)",
        ),
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
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = ctx["days"]
    if days < 1:
        raise IncompleteWebRequest("Days argument needs to be positive.")
    days2 = ctx["days2"]
    _days2 = days2 if days2 > 0 else 1
    days3 = ctx["days3"]
    _days3 = days3 if days3 > 0 else 1
    sts = ctx["sdate"]
    ets = ctx["edate"]
    if ets < sts:
        sts, ets = ets, sts
    yrrange = ets.year - sts.year
    year2 = ctx.get("year2")  # could be null!
    year3 = ctx.get("year3")  # could be null!
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
        WITH agg as (
            SELECT o.day, o.sday,
            avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as avgt,
            sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as sump,
            count(*) OVER (ORDER by day ASC ROWS %s PRECEDING) as cnt,
            avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as avgt2,
            sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as sump2,
            count(*) OVER (ORDER by day ASC ROWS %s PRECEDING) as cnt2,
            avg(high) OVER (ORDER by day ASC ROWS %s PRECEDING) as avgt3,
            sum(precip) OVER (ORDER by day ASC ROWS %s PRECEDING) as sump3,
            count(*) OVER (ORDER by day ASC ROWS %s PRECEDING) as cnt3
            from alldata o WHERE station = %s),
        agg2 as (
            SELECT sday,
            avg(avgt) as avg_avgt, stddev(avgt) as std_avgt,
            avg(sump) as avg_sump, stddev(sump) as std_sump,
            avg(avgt2) as avg_avgt2, stddev(avgt2) as std_avgt2,
            avg(sump2) as avg_sump2, stddev(sump2) as std_sump2,
            avg(avgt3) as avg_avgt3, stddev(avgt3) as std_avgt3,
            avg(sump3) as avg_sump3, stddev(sump3) as std_sump3
            from agg WHERE cnt = %s GROUP by sday)

        SELECT day,
        (a.avgt - b.avg_avgt) / b.std_avgt as t,
        (a.sump - b.avg_sump) / greatest(b.std_sump, 0.01) as p,
        (a.avgt2 - b.avg_avgt2) / b.std_avgt2 as t2,
        (a.sump2 - b.avg_sump2) / greatest(b.std_sump2, 0.01) as p2,
        (a.avgt3 - b.avg_avgt3) / b.std_avgt3 as t3,
        (a.sump3 - b.avg_sump3) / greatest(b.std_sump3, 0.01) as p3
        from agg a JOIN agg2 b on (a.sday = b.sday)
        ORDER by day ASC
        """,
            conn,
            params=(
                days - 1,
                days - 1,
                days - 1,
                _days2 - 1,
                _days2 - 1,
                _days2 - 1,
                _days3 - 1,
                _days3 - 1,
                _days3 - 1,
                station,
                days,
            ),
            index_col="day",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["aridity"] = df["t"] - df["p"]
    df["aridity2"] = df["t2"] - df["p2"]
    df["aridity3"] = df["t3"] - df["p3"]
    title = "" if year2 is None else f"{days} Day"
    title = (
        f"{ctx['_sname']} {title} Aridity Index\n"
        "Std. High Temp Departure minus Std. Precip Departure"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)

    if year2 is None:
        df2 = df.loc[sts:ets]
        ax.plot(
            df2.index.values,
            df2["aridity"],
            color="r",
            lw=2,
            label=f"{days} days",
        )
        maxval = df2["aridity"].abs().max() + 0.25
        if days2 > 0:
            ax.plot(
                df2.index.values,
                df2["aridity2"],
                color="b",
                lw=2,
                label=f"{days2} days",
            )
            maxval = max([maxval, df2["aridity2"].abs().max() + 0.25])
        if days3 > 0:
            ax.plot(
                df2.index.values,
                df2["aridity3"],
                color="g",
                lw=2,
                label=f"{days3} days",
            )
            maxval = max([maxval, df2["aridity3"].abs().max() + 0.25])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    else:
        df2 = df.loc[sts:ets]
        ax.plot(
            np.arange(len(df2.index)),
            df2["aridity"],
            color="r",
            lw=2,
            label=f"{ets.year}",
        )
        maxval = df2["aridity"].abs().max() + 0.25
        if year2 is not None:
            sts2 = sts.replace(year=year2 - yrrange)
            ets2 = ets.replace(year=year2)
            xticks = []
            xticklabels = []
            now = sts2
            i = 0
            while now < ets2:
                if now.day == 1:
                    xticks.append(i)
                    xticklabels.append(now.strftime("%b"))
                i += 1
                now += timedelta(days=1)
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels)
            df2 = df.loc[sts2:ets2]
            ax.plot(
                np.arange(len(df2.index)),
                df2["aridity"],
                color="b",
                lw=2,
                label=f"{year2}",
            )
            maxval = max([maxval, df2["aridity"].abs().max() + 0.25])
        if year3 is not None:
            sts2 = sts.replace(year=year3 - yrrange)
            ets2 = ets.replace(year=year3)
            df2 = df.loc[sts2:ets2]
            ax.plot(
                np.arange(len(df2.index)),
                df2["aridity"],
                color="g",
                lw=2,
                label=f"{year3}",
            )
            maxval = max([maxval, df2["aridity"].abs().max() + 0.25])

        # Compute year of best fit
        aridity = df.loc[sts:ets, "aridity"].values
        mae = 100
        useyear = None
        for _year in range(1951, date.today().year + 1):
            if _year == ets.year:
                continue
            sts2 = sts.replace(year=_year - yrrange)
            ets2 = ets.replace(year=_year)
            aridity2 = df.loc[sts2:ets2, "aridity"].values
            sz = min([len(aridity2), len(aridity)])
            error = (np.mean((aridity2[:sz] - aridity[:sz]) ** 2)) ** 0.5
            if error < mae:
                mae = error
                useyear = _year
        if useyear:
            sts2 = sts.replace(year=useyear - yrrange)
            ets2 = ets.replace(year=useyear)
            df2 = df.loc[sts2:ets2]
            ax.plot(
                np.arange(len(df2.index)),
                df2["aridity"],
                color="k",
                lw=2,
                label=f"{useyear} ({ets.year} best match)",
            )
            maxval = max([maxval, df2["aridity"].abs().max() + 0.25])
        ax.set_xlabel(f"{sts:%-d %b} to {ets:%-d %b}")
    ax.grid(True)

    if not pd.isna(maxval):
        ax.set_ylim(0 - maxval, maxval)
    ax.set_ylabel("Aridity Index")
    ax.text(
        1.01,
        0.75,
        "<-- More Water Stress",
        ha="left",
        va="center",
        transform=ax.transAxes,
        rotation=-90,
    )
    ax.text(
        1.01,
        0.25,
        "Less Water Stress -->",
        ha="left",
        va="center",
        transform=ax.transAxes,
        rotation=-90,
    )
    ax.legend(ncol=4, loc="best", fontsize=10)
    return fig, df
