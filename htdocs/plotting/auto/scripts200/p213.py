"""
This application generates percentiles based on available data
from the selected station.  These types of applications are good at
identifying bad data :(.  The date you select is used to generate the
bottom panel of explicit percentiles for the period of interest.  The
week is computed for the ISO-8601 week.

<p>If you generate this plot with the "year" option selected, you may
get an unexpected result.  The percentiles are computed over the entire
year which means that about everything during the summer is near the top
and everything during winter is near the bottom.  More understandable
results are found with shorter time windows of time to compute the
percentiles.
"""

import datetime
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.colorbar import ColorbarBase
from matplotlib.font_manager import FontProperties
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, get_cmap
from pyiem.plot.util import fitbox
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "tmpf": "Air Temperature [F]",
    "dwpf": "Dew Point Temperature [F]",
    "feel": "Feels Like Temperature [F]",
    "relh": "Relative Humidity [%]",
}
PDICT2 = {
    "day": "Percentiles for Date:",
    "week": "Percentiles for Week of Year Near:",
    "month": "Percentiles for Month:",
    "year": "Percentiles for Entire Year",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
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


def print_table(fig, df, varname):
    """Add a pretty table."""
    monofont = FontProperties(family="monospace")
    ranks = df[varname].quantile(np.arange(0, 1.0001, 0.0025))
    xpos = 0.72
    ypos = 0.8
    fitbox(
        fig,
        "Raw Percentiles (All Hours)",
        0.7,
        0.91,
        ypos + 0.01,
        ypos + 0.1,
        ha="center",
        va="center",
    )
    fig.text(xpos - 0.01, ypos - 0.01, "Percentile   Value")
    for q, val in ranks.items():
        if 0.02 < q < 0.98 and (q * 100.0 % 5) != 0:
            continue
        if abs(q - 0.5) < 0.001:
            xpos = 0.85
            ypos = 0.8
            fig.text(xpos - 0.01, ypos - 0.01, "Percentile   Value")
        ypos -= 0.035
        label = f"{q * 100:-6g} {val:-6.2f}"
        fig.text(xpos, ypos, label, fontproperties=monofont)


def plotter(fdict):
    """Go"""
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
        datefmt = "%-d %b\n%-I %p"
    else:
        subtitle = f"All Year, {date.year} plotted in bottom panel"
        datefmt = "%-d %b"

    # Load up all the values, since we need pandas to do some heavy lifting
    with get_sqlalchemy_conn("asos") as conn:
        obsdf = pd.read_sql(
            f"""
            select valid at time zone 'UTC' as utc_valid,
            extract(year from valid at time zone %s)::int as year,
            extract(hour from valid at time zone %s +
                '10 minutes'::interval)::int as hr, {varname}
            from alldata WHERE station = %s and {varname} is not null {limiter}
            and report_type = 3 ORDER by valid ASC
        """,
            conn,
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
    title = (
        f"{station} {ctx['_nt'].sts[station]['name']} {PDICT[varname]} "
        f"Percentiles ({obsdf['year'].min():.0f}-{obsdf['year'].max():.0f})\n"
        f"{subtitle}"
    )
    fig = figure(apctx=ctx, title=title)
    tp = fig.add_axes([0.1, 0.57, 0.5, 0.33])
    bp = fig.add_axes([0.1, 0.13, 0.5, 0.35])
    sidep = fig.add_axes([0.61, 0.13, 0.1, 0.35])
    # Plot total percentiles on the figure
    print_table(fig, obsdf, varname)
    cmap = get_cmap(ctx["cmap"])
    for hr, gdf in qtile.groupby("hr"):
        tp.plot(
            gdf["quantile"].values * 100.0,
            gdf[varname].values,
            color=cmap(hr / 23.0),
            label=str(hr),
        )
    tp.set_xlim(0, 100)
    tp.set_xticks([0, 10, 25, 50, 75, 90, 100])
    tp.grid(True)
    tp.set_ylabel(PDICT[varname])
    tp.set_xlabel("Percentile")
    cax = fig.add_axes(
        [0.613, 0.55, 0.01, 0.33], frameon=False, yticks=[], xticks=[]
    )
    cb = ColorbarBase(cax, cmap=cmap)
    cb.set_ticks(np.arange(0, 1, 4.0 / 24.0))
    cb.set_ticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    cb.set_label("Local Hour")

    thisyear = obsdf[obsdf["year"] == date.year]
    if not thisyear.empty:
        bp.plot(
            thisyear["utc_valid"].values, thisyear["quantile"].values * 100.0
        )
        bp.grid(True)
        bp.set_ylabel("Percentile")
        bp.set_yticks([0, 10, 25, 50, 75, 90, 100])
        bp.set_ylim(-1, 101)
        bp.xaxis.set_major_formatter(
            mdates.DateFormatter(datefmt, tz=ZoneInfo(tzname))
        )
        if opt == "day":
            bp.set_xlabel(f"Timezone: {tzname}")
        # Add horizontal bar graph with a histogram of the percentiles
        hist = np.histogram(
            thisyear["quantile"].values * 100.0,
            bins=np.arange(0, 101, 10),
        )
        sidep.barh(
            hist[1][:-1],
            hist[0],
            height=10,
            align="edge",
        )
        sidep.set_xlabel("Hours")
        sidep.set_yticks([])
        sidep.set_ylim(-1, 101)
        sidep.grid(True)
        sidep.text(0.1, 1.01, "Histogram", transform=sidep.transAxes)

    return fig, qtile


if __name__ == "__main__":
    plotter({})
