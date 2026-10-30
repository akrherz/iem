"""
This chart presents the hourly average wind speeds
by month of the year or by custom periods.
The hours presented are valid in the local time zone
of the reporting station.  For example in Iowa, 3 PM would represent
3 PM CDT in the summer and 3 PM CST in the winter.  Please complain to us
if this logic causes you heartburn!  The format of the date periods is
two digit month followed by two digit day for both the start and end
date.
"""

import calendar
from datetime import date, datetime
from typing import Annotated

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest, NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import convert_value

from iemweb.autoplot.description import (
    PlotDescription,
    SelectArg,
    TextArg,
    YearArg,
    ZStationArg,
)
from iemweb.autoplot.params import AutoplotParams

UNITS = {"mph": "miles per hour", "kt": "knots", "mps": "meters per second"}
UNITCONV = {"mph": "mile / hour", "kt": "knot", "mps": "meter / second"}


class Params(AutoplotParams):
    """Request parameters."""

    zstation: Annotated[
        str, ZStationArg(label="Select Station:", network="IA_ASOS")
    ] = "AMW"
    units: Annotated[
        str, SelectArg(options=UNITS, label="Units of Average Wind Speed")
    ] = "mph"
    p1: Annotated[
        str | None,
        TextArg(
            label="Optional. Average for inclusive period of days",
            default="0501-0510",
        ),
    ] = None
    p2: Annotated[
        str | None,
        TextArg(
            label="Optional. Average for inclusive period of days",
            default="0511-0520",
        ),
    ] = None
    p3: Annotated[
        str | None,
        TextArg(
            label="Optional. Average for inclusive period of days",
            default="0521-0530",
        ),
    ] = None
    p4: Annotated[
        str | None,
        TextArg(
            label="Optional. Average for inclusive period of days",
            default="0601-0610",
        ),
    ] = None
    p5: Annotated[
        str | None,
        TextArg(
            label="Optional. Average for inclusive period of days",
            default="0611-0620",
        ),
    ] = None
    p6: Annotated[
        str | None,
        TextArg(
            label="Optional. Average for inclusive period of days",
            default="0621-0630",
        ),
    ] = None
    y1: Annotated[
        int | None,
        YearArg(
            label="Optional. Limit Period of Record to inclusive start year",
            default=1973,
        ),
    ] = None
    y2: Annotated[
        int | None,
        YearArg(
            label="Optional. Limit Period of Record to inclusive end year",
            default=lambda: date.today().year,
        ),
    ] = None


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, cache=86400
    )


def add_context(ctx: Params):
    """get context for both output types"""
    station = ctx.zstation
    ctx["station"] = station
    units = ctx.units
    p1 = ctx.p1
    p2 = ctx.p2
    p3 = ctx.p3
    p4 = ctx.p4
    p5 = ctx.p5
    p6 = ctx.p6
    y1 = ctx.y1
    y2 = ctx.y2

    ylimiter = ""
    if y1 is not None and y2 is not None:
        ylimiter = (
            f" and extract(year from valid) >= {y1} and "
            f"extract(year from valid) <= {y2} "
        )
    else:
        ab = ctx["_nt"].sts[station]["archive_begin"]
        if ab is None:
            raise NoDataFound("Unknown station metadata.")
        y1 = ab.year
        y2 = date.today().year

    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        WITH obs as (
            SELECT (valid + '10 minutes'::interval) at time zone :tzname as ts,
            sknt from alldata where station = :station and sknt >= 0
            and sknt < 150 and report_type = 3 {ylimiter})

        select extract(month from ts)::int as month,
        extract(hour from ts)::int as hour, extract(day from ts)::int as day,
        avg(sknt) as avg_sknt from obs GROUP by month, day, hour
        ORDER by month, day, hour
            """,
                ylimiter=ylimiter,
            ),
            conn,
            params={
                "tzname": ctx["_nt"].sts[station]["tzname"],
                "station": station,
            },
            index_col=None,
        )
    # Figure out which mode we are going to do
    if all(a is None for a in [p1, p2, p3, p4, p5, p6]):
        df = (
            df.drop(columns="day")
            .groupby(["month", "hour"])
            .mean()
            .reset_index()
        )
        ctx["ncols"] = 6
        ctx["labels"] = calendar.month_abbr
        ctx["subtitle"] = "Monthly Average Wind Speed by Hour"
    else:
        ctx["ncols"] = 3
        df["fake_date"] = pd.to_datetime(
            {
                "year": np.ones(len(df.index)) * 2000,
                "month": df["month"].to_numpy(),
                "day": df["day"].to_numpy(),
            }
        )
        df = df.set_index("fake_date")
        dfs = []
        ctx["labels"] = [None]
        for p in [p1, p2, p3, p4, p5, p6]:
            if p is None:
                continue
            tokens = p.split("-")
            if len(tokens) != 2 or len(tokens[0]) != 4 or len(tokens[1]) != 4:
                raise IncompleteWebRequest("Invalid date period format.")
            sts = datetime.strptime(f"2000{tokens[0].strip()}", "%Y%m%d")
            ets = datetime.strptime(f"2000{tokens[1].strip()}", "%Y%m%d")
            ldf = (
                df[["hour", "avg_sknt"]]
                .loc[pd.Timestamp(sts) : pd.Timestamp(ets)]
                .groupby("hour")
                .mean()
            )
            ldf = ldf.reset_index()
            ldf["month"] = len(dfs) + 1
            dfs.append(ldf)
            ctx["labels"].append(f"{sts:%b%d}-{ets:%b%d}")
            ctx["subtitle"] = "Period Average Wind Speed by Hour"
        df = pd.concat(dfs)

    df[f"avg_{units}"] = convert_value(
        df["avg_sknt"].values, "knot", UNITCONV[units]
    )
    ctx["df"] = df
    ctx["ylabel"] = "Average Wind Speed [%s]" % (UNITS[units],)
    ctx["xlabel"] = ("Hour of Day (timezone: %s)") % (
        ctx["_nt"].sts[station]["tzname"],
    )
    ctx["title"] = f"{ctx.sname} [{y1}-{y2}]"


def get_highcharts(ctx: Params) -> str:
    """highcharts output"""
    add_context(ctx)
    lines = []
    dash_styles = ["Solid", "ShortDash"]
    for month, df2 in ctx["df"].groupby("month"):
        v = df2[["hour", f"avg_{ctx.units}"]].to_json(orient="values")
        lines.append(
            f"""
{{
    name: '{ctx["labels"][month]}',
    type: 'line',
    dashStyle: '{dash_styles[(month - 1) // 6]}',
    tooltip: {{valueDecimals: 1}},
    data: {v}
}}
        """
        )
    series = ",".join(lines)
    containername = ctx["_e"]
    return f"""
Highcharts.chart('{containername}', {{
    chart: {{
        type: 'column'
    }},
    xAxis: {{
        categories: ['Mid', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
    '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 'Noon', '1 PM',
    '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM',
    '10 PM', '11 PM'],
        title: {{text: '{ctx["xlabel"]}'}}
    }},
    legend: {{
        itemDistance: 50,
        symbolWidth: 40,
    }},
    tooltip: {{shared: true}},
    yAxis: {{
        title: {{text: '{ctx["ylabel"]}'}}
    }},
    title: {{text: '{ctx["title"]}'}},
    subtitle: {{text: '{ctx["subtitle"]}'}},
    series: [{series}]
}});
"""


def plotter(ctx: Params):
    """Go"""
    add_context(ctx)
    (fig, ax) = figure_axes(
        apctx=ctx, title=ctx["title"], subtitle=ctx["subtitle"]
    )
    colors = [
        None,
        "k",
        "k",
        "r",
        "r",
        "b",
        "b",
        "tan",
        "tan",
        "purple",
        "purple",
        "brown",
        "brown",
    ]
    styles = ["-", "--"]
    for month, df2 in ctx["df"].groupby("month"):
        ax.plot(
            df2["hour"].values,
            df2["avg_%s" % (ctx.units,)],
            label=ctx["labels"][month],
            lw=2,
            color=colors[month],
            linestyle=styles[month % 2],
        )
    ax.set_ylabel(ctx["ylabel"])
    ax.grid(True)
    ax.set_position([0.1, 0.25, 0.85, 0.65])
    ax.legend(
        ncol=ctx["ncols"],
        bbox_to_anchor=(0.5, -0.22),
        fontsize=10,
        loc="center",
    )
    ax.set_xlabel(ctx["xlabel"])
    ax.set_xticks(range(0, 24, 4))
    ax.set_xticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    ax.set_xlim(0, 23)

    return fig, ctx["df"]
