"""Aridity"""
import datetime

from pandas.io.sql import read_sql
import numpy as np
import matplotlib.dates as mdates
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """
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
    today = datetime.date.today()
    sts = today - datetime.timedelta(days=180)
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            network="IACLIMATE",
            label="Select Station:",
        ),
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
    days2 = ctx["days2"]
    _days2 = days2 if days2 > 0 else 1
    days3 = ctx["days3"]
    _days3 = days3 if days3 > 0 else 1
    sts = ctx["sdate"]
    ets = ctx["edate"]
    yrrange = ets.year - sts.year
    year2 = ctx.get("year2")  # could be null!
    year3 = ctx.get("year3")  # could be null!
    pgconn = get_dbconn("coop")

    table = "alldata_%s" % (station[:2],)
    df = read_sql(
        f"""
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
        from {table} o WHERE station = %s),
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
    (a.sump - b.avg_sump) / b.std_sump as p,
    (a.avgt2 - b.avg_avgt2) / b.std_avgt2 as t2,
    (a.sump2 - b.avg_sump2) / b.std_sump2 as p2,
    (a.avgt3 - b.avg_avgt3) / b.std_avgt3 as t3,
    (a.sump3 - b.avg_sump3) / b.std_sump3 as p3
    from agg a JOIN agg2 b on (a.sday = b.sday)
    ORDER by day ASC
    """,
        pgconn,
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
    (fig, ax) = figure_axes(apctx=ctx)

    if year2 is None:
        df2 = df.loc[sts:ets]
        ax.plot(
            df2.index.values,
            df2["aridity"],
            color="r",
            lw=2,
            label="%s days" % (days,),
        )
        maxval = df2["aridity"].abs().max() + 0.25
        if days2 > 0:
            ax.plot(
                df2.index.values,
                df2["aridity2"],
                color="b",
                lw=2,
                label="%s days" % (days2,),
            )
            maxval = max([maxval, df2["aridity2"].abs().max() + 0.25])
        if days3 > 0:
            ax.plot(
                df2.index.values,
                df2["aridity3"],
                color="g",
                lw=2,
                label="%s days" % (days3,),
            )
            maxval = max([maxval, df2["aridity3"].abs().max() + 0.25])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
        title = ""
    else:
        df2 = df.loc[sts:ets]
        ax.plot(
            np.arange(len(df2.index)),
            df2["aridity"],
            color="r",
            lw=2,
            label="%s" % (ets.year,),
        )
        maxval = df2["aridity"].abs().max() + 0.25
        if year2 is not None:
            sts2 = sts.replace(year=(year2 - yrrange))
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
                now += datetime.timedelta(days=1)
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels)
            df2 = df.loc[sts2:ets2]
            ax.plot(
                np.arange(len(df2.index)),
                df2["aridity"],
                color="b",
                lw=2,
                label="%s" % (year2,),
            )
            maxval = max([maxval, df2["aridity"].abs().max() + 0.25])
        if year3 is not None:
            sts2 = sts.replace(year=(year3 - yrrange))
            ets2 = ets.replace(year=year3)
            df2 = df.loc[sts2:ets2]
            ax.plot(
                np.arange(len(df2.index)),
                df2["aridity"],
                color="g",
                lw=2,
                label="%s" % (year3,),
            )
            maxval = max([maxval, df2["aridity"].abs().max() + 0.25])

        # Compute year of best fit
        aridity = df.loc[sts:ets, "aridity"].values
        mae = 100
        useyear = None
        for _year in range(1951, datetime.date.today().year + 1):
            if _year == ets.year:
                continue
            sts2 = sts.replace(year=(_year - yrrange))
            ets2 = ets.replace(year=_year)
            aridity2 = df.loc[sts2:ets2, "aridity"].values
            sz = min([len(aridity2), len(aridity)])
            error = (np.mean((aridity2[:sz] - aridity[:sz]) ** 2)) ** 0.5
            if error < mae:
                mae = error
                useyear = _year
        if useyear:
            sts2 = sts.replace(year=(useyear - yrrange))
            ets2 = ets.replace(year=useyear)
            df2 = df.loc[sts2:ets2]
            ax.plot(
                np.arange(len(df2.index)),
                df2["aridity"],
                color="k",
                lw=2,
                label="%s (%s best match)" % (useyear, ets.year),
            )
            maxval = max([maxval, df2["aridity"].abs().max() + 0.25])
        title = "%s Day" % (days,)
        ax.set_xlabel(
            "%s to %s" % (sts.strftime("%-d %b"), ets.strftime("%-d %b"))
        )
    ax.grid(True)
    ax.set_title(
        (
            "%s [%s] %s Aridity Index\n"
            "Std. High Temp Departure minus Std. Precip Departure"
        )
        % (ctx["_nt"].sts[station]["name"], station, title)
    )
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


if __name__ == "__main__":
    plotter(dict())
