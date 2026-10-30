"""
This chart presents the accumulated frequency of
having the last spring temperature at or below a given threshold.

<p><a href="/plotting/auto/?q=119">Autoplot 119</a> is closely related to this
autoplot and presents the fall season values.</p>
"""

from datetime import date, timedelta
from typing import Annotated

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import IntArg, PlotDescription, YearArg
from iemweb.autoplot.params import AutoplotParams


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    t1: Annotated[int, IntArg(label="First Threshold (°F)")] = 32
    t2: Annotated[int, IntArg(label="Second Threshold (°F)")] = 28
    t3: Annotated[int, IntArg(label="Third Threshold (°F)")] = 26
    t4: Annotated[int, IntArg(label="Fourth Threshold (°F)")] = 22
    syear: Annotated[
        int, YearArg(min=1880, label="Potential (if data exists) minimum year")
    ] = 1880
    eyear: Annotated[
        int,
        YearArg(
            min=1880,
            label="Potential (if data exists) exclusive maximum year",
            default=lambda: date.today().year,
        ),
    ]


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, report=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    thresholds = [ctx.t1, ctx.t2, ctx.t3, ctx.t4]

    df = pd.DataFrame(
        {
            "dates": pd.date_range("2000/01/29", "2000/06/30"),
            f"{thresholds[0]}cnts": 0,
            f"{thresholds[1]}cnts": 0,
            f"{thresholds[2]}cnts": 0,
            f"{thresholds[3]}cnts": 0,
        },
        index=range(29, 183),
    )
    df.index.name = "doy"

    for base in thresholds:
        # Query Last doy for each year in archive
        with get_sqlalchemy_conn("coop") as conn:
            df2 = pd.read_sql(
                """
                select year,
                max(case when low <= %s then extract(doy from day)
                    else 0 end) as doy from alldata
                WHERE month < 7 and station = %s and year > %s and year < %s
                GROUP by year
            """,
                conn,
                params=(base, station, ctx.syear, ctx.eyear),
                index_col=None,
            )
        for _, row in df2.iterrows():
            if row["doy"] == 0:
                continue
            df.loc[0 : row["doy"], "%scnts" % (base,)] += 1
        df["%sfreq" % (base,)] = (
            df["%scnts" % (base,)] / len(df2.index) * 100.0
        )

    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("No metadata found.")
    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# Low Temperature exceedence probabilities
# (On a certain date, what is the chance a temperature below a certain
# threshold would be observed again that spring season)
 DOY Date    <%s  <%s  <%s  <%s
""" % (
        date.today().strftime("%d %b %Y"),
        max([bs, date(ctx.syear, 1, 1)]),
        min([date.today(), date(ctx.eyear - 1, 12, 31)]),
        ctx.sname,
        thresholds[0] + 1,
        thresholds[1] + 1,
        thresholds[2] + 1,
        thresholds[3] + 1,
    )
    fcols = ["%sfreq" % (s,) for s in thresholds]
    mindate = None
    for doy, row in df.iterrows():
        if doy % 2 != 0:
            continue
        if row[fcols[3]] < 100 and mindate is None:
            mindate = row["dates"] - timedelta(days=5)
        res += (" %3s %s  %3i  %3i  %3i  %3i\n") % (
            row["dates"].strftime("%-j"),
            row["dates"].strftime("%b %d"),
            row[fcols[0]],
            row[fcols[1]],
            row[fcols[2]],
            row[fcols[3]],
        )

    title = "Frequency of Last Spring Temperature"
    subtitle = "%s %s (%s-%s)" % (
        station,
        ctx["_nt"].sts[station]["name"],
        max([bs, date(ctx.syear, 1, 1)]),
        min([date.today(), date(ctx.eyear - 1, 12, 31)]),
    )
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    for base in thresholds:
        ax.plot(
            df["dates"].values,
            df[f"{base}freq"],
            label=f"{base}",
            lw=2,
        )

    ax.legend(loc="best")
    ax.set_xlim(mindate)
    ax.xaxis.set_major_locator(mdates.DayLocator([1, 7, 14, 21]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    ax.grid(True)
    df = df.reset_index()
    return fig, df, res
