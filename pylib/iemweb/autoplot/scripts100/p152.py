"""
This map produces an analysis of change in
the number of days for the growing season. This is defined by the period
between the last spring low temperature below 32 degrees and the first fall
date below 32 degrees.  This analysis tends to be very noisy, so picking
longer periods of time for each period will help some.
"""

from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, centered_bins, get_cmap
from pyiem.reference import SECTORS_NAME

from iemweb.autoplot.description import (
    CmapArg,
    PlotDescription,
    SelectArg,
    StateArg,
    YearArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {"state": "State Level Maps (select state)"}
PDICT.update(SECTORS_NAME)
PDICT2 = {
    "both": "Show both contour and values",
    "values": "Show just the values",
    "contour": "Show just the contour",
}
PDICT3 = {
    "season": "Number of Days in Growing Season",
    "spring": "Date of Last Spring Freeze",
    "fall": "Date of First Fall Freeze",
}


class Params(AutoplotParams):
    """Request parameters."""

    sector: Annotated[
        str, SelectArg(options=PDICT, label="Select Map Region")
    ] = "state"
    state: Annotated[
        str, StateArg(label="Select State to Plot (when appropriate)")
    ] = "IA"
    opt: Annotated[
        str, SelectArg(options=PDICT2, label="Map Plot/Contour View Option")
    ] = "both"
    var: Annotated[
        str, SelectArg(options=PDICT3, label="Variable to Plot")
    ] = "season"
    p1syear: Annotated[
        int, YearArg(label="Start Year (inclusive) of Period One:")
    ] = 1951
    p1eyear: Annotated[
        int, YearArg(label="End Year (inclusive) of Period One:")
    ] = 1980
    p2syear: Annotated[
        int, YearArg(label="Start Year (inclusive) of Period Two:")
    ] = 1981
    p2eyear: Annotated[
        int, YearArg(label="End Year (inclusive) of Period Two:")
    ] = 2010
    cmap: Annotated[str, CmapArg(label="Color Ramp:")] = "seismic"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    state = ctx.state[:2]
    sector = ctx.sector
    opt = ctx.opt
    p1syear = ctx.p1syear
    p1eyear = ctx.p1eyear
    p2syear = ctx.p2syear
    p2eyear = ctx.p2eyear
    varname = ctx.var

    table = "alldata"
    if sector == "state":
        table = f"alldata_{state.lower()}"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        WITH season1 as (
            SELECT station, year,
            min(case when month > 7 and low < 32 then
                extract(doy from day) else 366 end) as first_freeze,
            max(case when month < 7 and low < 32 then
                extract(doy from day) else 0 end) as last_freeze
            from {table} WHERE
            year >= :p1syear and year <= :p1eyear GROUP by station, year),
        season2 as (
            SELECT station, year,
            min(case when month > 7 and low < 32 then
                extract(doy from day) else 366 end) as first_freeze,
            max(case when month < 7 and low < 32 then
                extract(doy from day) else 0 end) as last_freeze
            from {table} WHERE
            year >= :p2syear and year <= :p2eyear GROUP by station, year),
        agg1 as (
            SELECT station as p1station, avg(first_freeze) as p1_first_fall,
            avg(last_freeze) as p1_last_spring,
            count(first_freeze) as p1_count
            from season1 GROUP by station),
        agg2 as (
            SELECT station as p2station, avg(first_freeze) as p2_first_fall,
            avg(last_freeze) as p2_last_spring,
            count(first_freeze) as p2_count
            from season2 GROUP by station),
        agg as (
            SELECT a.p1station as station, p1_first_fall, p1_last_spring,
            p2_first_fall, p2_last_spring, p1_count, p2_count
            from agg1 a JOIN agg2 b on (a.p1station = b.p2station) WHERE
            p1_count > :p1quorum and p2_count > :p2quorum
        )
        SELECT ST_X(geom) as lon, ST_Y(geom) as lat,
        d.* from agg d JOIN stations t ON (d.station = t.id)
        WHERE t.network ~* 'CLIMATE'
        and substr(station, 3, 1) not in ('C', 'D')
        and substr(station, 3, 4) != '0000'
        """,
                table=table,
            ),
            conn,
            params={
                "p1syear": p1syear,
                "p1eyear": p1eyear,
                "p2syear": p2syear,
                "p2eyear": p2eyear,
                "p1quorum": (p1eyear - p1syear) - 2,
                "p2quorum": (p2eyear - p2syear) - 2,
            },
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found")
    df["p1_season"] = df["p1_first_fall"] - df["p1_last_spring"]
    df["p2_season"] = df["p2_first_fall"] - df["p2_last_spring"]
    df["season_delta"] = df["p2_season"] - df["p1_season"]
    df["spring_delta"] = df["p2_last_spring"] - df["p1_last_spring"]
    df["fall_delta"] = df["p2_first_fall"] - df["p1_first_fall"]
    # Reindex so that most extreme values are first
    df = df.reindex(
        df[f"{varname}_delta"].abs().sort_values(ascending=False).index
    )

    title = PDICT3[varname]
    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=state,
        axisbg="white",
        title=(
            f"{p2syear:.0f}-{p2eyear:.0f} minus {p1syear:.0f}-"
            f"{p1eyear:.0f} {title} Difference"
        ),
        subtitle="based on IEM Archives",
        titlefontsize=14,
        nocaption=True,
    )
    # Create 9 levels centered on zero
    abval = df[varname + "_delta"].abs().max()
    levels = centered_bins(abval)
    if opt in ["both", "contour"] and len(levels) > 1:
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df[f"{varname}_delta"].values,
            levels,
            cmap=get_cmap(ctx.cmap),
            units="days",
        )
    if sector == "state":
        mp.drawcounties()
    if opt in ["both", "values"]:
        mp.plot_values(
            df["lon"].values,
            df["lat"].values,
            df[f"{varname}_delta"].values,
            fmt="%.1f",
            labelbuffer=5,
        )

    return mp.fig, df
