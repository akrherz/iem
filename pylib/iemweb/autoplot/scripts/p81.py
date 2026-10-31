"""
This chart presents two measures of temperature
variability.  The first is the standard deviation of the period of
record for a given day of the year.  The second is the standard deviation
of the day to day changes in temperature.
"""

import calendar
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import PlotDescription, SelectArg
from iemweb.autoplot.params import AutoplotParams

PDICT = {"high": "High Temperature", "low": "Low Temperature"}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    var: Annotated[
        str, SelectArg(label="Which Daily Variable:", options=PDICT)
    ] = "high"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    varname = ctx.var[:10]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        with data as (
            select extract(doy from day) as doy,
            day, {varname} as v from alldata WHERE
            station = :station),
        doyagg as (
            SELECT doy, stddev(v) from data GROUP by doy),
        deltas as (
            SELECT doy, (v - lag(v) OVER (ORDER by day ASC)) as d from data),
        deltaagg as (
            SELECT doy, stddev(d) from deltas GROUP by doy)

        SELECT d.doy, d.stddev as d2d_stddev,
        y.stddev as doy_stddev from deltaagg d JOIN doyagg y ON
        (y.doy = d.doy) WHERE d.doy < 366 ORDER by d.doy ASC
        """,
                varname=varname,
            ),
            conn,
            params={"station": station},
            index_col="doy",
        )

    title = f"{ctx.sname} :: Daily {PDICT.get(varname)} Standard Deviations"
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1, sharex=True)
    ax[0].plot(
        df.index.values, df["doy_stddev"], lw=2, color="r", label="Single Day"
    )
    ax[0].plot(
        df.index.values, df["d2d_stddev"], lw=2, color="b", label="Day to Day"
    )
    ax[0].legend(loc="best", fontsize=10, ncol=2)

    ax[0].set_ylabel("Temperature Std. Deviation °F")
    ax[0].grid(True)

    ax[1].plot(
        df.index.values, df["doy_stddev"] / df["d2d_stddev"], lw=2, color="g"
    )
    ax[1].set_ylabel("Ratio SingleDay/Day2Day")
    ax[1].grid(True)
    ax[1].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].set_xlim(0, 366)
    return fig, df
