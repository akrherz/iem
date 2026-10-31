"""
This plot displays the frequency of a daily high
or low temperature being within a certain bounds of the long term NCEI
climatology for the location.
"""

import calendar
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import IntArg, PlotDescription
from iemweb.autoplot.params import AutoplotParams

PDICT = {"high": "High temperature", "low": "Low Temperature"}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    min: Annotated[
        int, IntArg(label="Lower Bound (F) of Temperature Range")
    ] = -5
    max: Annotated[
        int, IntArg(label="Upper Bound (F) of Temperature Range")
    ] = 5


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    minv = ctx.min
    maxv = ctx.max
    if minv > maxv:
        minv, maxv = maxv, minv
    station = ctx.station
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
        WITH climate as (
            SELECT to_char(valid, 'mmdd') as sday, high, low from
            ncei_climate91 where station = :ncei
        )
        SELECT extract(doy from day) as doy, count(*),
        SUM(case when a.high >= (c.high + :minv) and a.high < (c.high + :maxv)
                then 1 else 0 end) as high_count,
        SUM(case when a.low >= (c.low + :minv) and a.low < (c.low + :maxv)
                then 1 else 0 end) as low_count
        FROM alldata a JOIN climate c on (a.sday = c.sday)
        WHERE a.sday != '0229' and station = :station
        GROUP by doy ORDER by doy ASC
        """),
            conn,
            params={
                "ncei": ctx["_nt"].sts[station]["ncei91"],
                "minv": minv,
                "maxv": maxv,
                "station": station,
            },
            index_col="doy",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    df["high_freq"] = df["high_count"] / df["count"] * 100.0
    df["low_freq"] = df["low_count"] / df["count"] * 100.0
    hvals = df["high_freq"].rolling(7, min_periods=1).mean().values
    lvals = df["low_freq"].rolling(7, min_periods=1).mean().values
    title = (
        f"{ctx.sname}\nFreq of Temp between {minv}°F and {maxv}°F "
        "of NCEI-81 Average"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    ax.plot(df.index.values, hvals, color="r", label="High", zorder=1)
    ax.plot(df.index.values, lvals, color="b", label="Low", zorder=1)
    ax.axhline(50, lw=2, color="green", zorder=2)
    ax.set_ylabel("Percentage of Years [%]")
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.legend(loc="best")
    ax.set_xlabel("* seven day smoother applied")
    ax.set_xlim(1, 367)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_ylim(0, 100)
    ax.grid(True)
    return fig, df
