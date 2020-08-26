"""Plot up some percentiles please."""
import datetime
from collections import OrderedDict

import pytz
import numpy as np
from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from matplotlib.colorbar import ColorbarBase

from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot import get_cmap
from pyiem.plot.use_agg import plt
from pyiem.plot.util import fitbox
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("tmpf", "Air Temperature [F]"),
        ("dwpf", "Dew Point Temperature [F]"),
        ("feel", "Feels Like Temperature [F]"),
        ("relh", "Relative Humidity [%]"),
    ]
)
PDICT2 = OrderedDict(
    [
        ("day", "Percentiles for Date:"),
        ("week", "Percentiles for Week of Year Near:"),
        ("month", "Percentiles for Month:"),
        ("year", "Percentiles for Entire Year"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This application generates percentiles based on available data
    from the selected station.  These types of applications are good at
    identifying bad data :(.  The date you select is used to generate the
    bottom panel of explicit percentiles for the period of interest.  The
    week is computed for the ISO-8601 week.

    <p>If you generate this plot with the "year" option selected, you may
    get an unexpected result.  The percentiles are computed over the entire
    year which means that about everything during the summer is near the top
    and everything during winter is near the bottom.  More understandable
    results are found with shorter time windows of time to compute the
    percentiles."""
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
            name="date",
            default=datetime.date.today().strftime("%Y/%m/%d"),
            label="Date of Interest (used to select week, month, year):",
        ),
        dict(
            type="select",
            name="v",
            default="tmpf",
            label="Variable to Compute Percentiles For:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="opt",
            default="month",
            label="Date Range to Compute Percentiles For:",
            options=PDICT2,
        ),
        dict(type="cmap", name="cmap", default="hsv", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("asos")

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    date = ctx["date"]
    opt = ctx["opt"]
    varname = ctx["v"]

    tzname = ctx["_nt"].sts[station]["tzname"]

    # Resolve how to limit the query data
    limiter = ""
    if opt == "day":
        limiter = (
            f" and to_char(valid at time zone '{tzname}', 'mmdd') = "
            f"'{date.strftime('%m%d')}' "
        )
        subtitle = (
            f"For Date of {date.strftime('%-d %b')}, "
            f"{date.strftime('%-d %b %Y')} plotted in bottom panel"
        )
        datefmt = "%I %p"
    elif opt == "week":
        limiter = f" and extract(week from valid) = {date.strftime('%V')} "
        subtitle = (
            f"For ISO Week of {date.strftime('%V')}, "
            f"week of {date.strftime('%-d %b %Y')} plotted in bottom panel"
        )
        datefmt = "%-d %b"
    elif opt == "month":
        limiter = f" and extract(month from valid) = {date.strftime('%m')} "
        subtitle = (
            f"For Month of {date.strftime('%B')}, "
            f"{date.strftime('%b %Y')} plotted in bottom panel"
        )
        datefmt = "%-d"
    else:
        subtitle = f"All Year, {date.year} plotted in bottom panel"
        datefmt = "%-d %b"

    # Load up all the values, since we need pandas to do some heavy lifting
    obsdf = read_sql(
        f"""
        select valid at time zone 'UTC' as utc_valid,
        extract(year from valid at time zone %s)  as year,
        extract(hour from valid at time zone %s +
            '10 minutes'::interval)::int as hr, {varname}
        from alldata WHERE station = %s and {varname} is not null {limiter}
        and report_type = 2 ORDER by valid ASC
    """,
        pgconn,
        params=(tzname, tzname, station),
        index_col=None,
    )
    if obsdf.empty:
        raise NoDataFound("No data was found.")

    # Assign percentiles
    obsdf["quantile"] = obsdf[["hr", varname]].groupby("hr").rank(pct=True)
    # Compute actual percentiles
    qtile = (
        obsdf[["hr", varname]]
        .groupby("hr")
        .quantile(np.arange(0, 1.01, 0.05))
        .reset_index()
    )
    qtile = qtile.rename(columns={"level_1": "quantile"})
    (fig, ax) = plt.subplots(2, 1)
    cmap = get_cmap(ctx["cmap"])
    for hr, gdf in qtile.groupby("hr"):
        ax[0].plot(
            gdf["quantile"].values * 100.0,
            gdf[varname].values,
            color=cmap(hr / 23.0),
            label=str(hr),
        )
    ax[0].set_xlim(0, 100)
    ax[0].grid(True)
    ax[0].set_ylabel(PDICT[varname])
    ax[0].set_xlabel("Percentile")
    ax[0].set_position([0.13, 0.55, 0.71, 0.34])
    cax = plt.axes(
        [0.86, 0.55, 0.03, 0.33], frameon=False, yticks=[], xticks=[]
    )
    cb = ColorbarBase(cax, cmap=cmap)
    cb.set_ticks(np.arange(0, 1, 4.0 / 24.0))
    cb.set_ticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    cb.set_label("Local Hour")

    thisyear = obsdf[obsdf["year"] == date.year]
    if not thisyear.empty:
        ax[1].plot(
            thisyear["utc_valid"].values, thisyear["quantile"].values * 100.0
        )
        ax[1].grid(True)
        ax[1].set_ylabel("Percentile")
        ax[1].set_ylim(-1, 101)
        ax[1].xaxis.set_major_formatter(
            mdates.DateFormatter(datefmt, tz=pytz.timezone(tzname))
        )
        if opt == "day":
            ax[1].set_xlabel(f"Timezone: {tzname}")
    title = ("%s %s %s Percentiles\n%s") % (
        station,
        ctx["_nt"].sts[station]["name"],
        PDICT[varname],
        subtitle,
    )
    fitbox(fig, title, 0.01, 0.99, 0.91, 0.99, ha="center", va="center")
    return fig, qtile


if __name__ == "__main__":
    plotter(dict())
