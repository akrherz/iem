"""
This autoplot can either produce a plot of averages for a given period or
annual over a period of years; or a difference between a second set of years.
<a href="/plotting/auto/?q=97">Autoplot 97</a> is a similar plot and perhaps
more useful for some users than this one.  <strong>This autoplot can be very
slow when plotting more than a single state of data.</strong>
"""

from datetime import date
from typing import Annotated

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, centered_bins, get_cmap
from pyiem.reference import SECTORS_NAME, Z_CLIP

from iemweb.autoplot.description import (
    CmapArg,
    FloatArg,
    PlotDescription,
    SDayArg,
    SelectArg,
    StateArg,
    YearArg,
)
from iemweb.autoplot.params import AutoplotParams
from iemweb.util import month2months

PDICT = {
    "state": "State Level Maps (select state)",
}
PDICT.update(SECTORS_NAME)

PDICT2 = {
    "both": "Show both contour and values",
    "values": "Show just the values",
    "contour": "Show just the contour",
}
PDICT3 = {
    "total_precip": "Total Precipitation",
    "gdd": "Growing Degree Days (base=50/86)",
    "sdd": "Stress Degree Days (High > 86)",
    "avg_temp": "Average Temperature",
    "avg_high": "Average High Temperature",
    "avg_low": "Average Low Temperature",
    "days_high_above": "Days with High Temp At or Above [Threshold]",
    "days_high_below": "Days with High Temp Below [Threshold]",
    "days_low_above": "Days with Low Temp At or Above [Threshold]",
    "days_low_below": "Days with Low Temp Below [Threshold]",
    "days_precip_above": "Days with Precipitation At or Above [Threshold]",
}
PDICT4 = {
    "english": "English",
    "metric": "Metric",
}
UNITS = {
    "total_precip": "inch",
    "gdd": "°F",
    "sdd": "°F",
    "avg_temp": "°F",
    "avg_high": "F",
    "avg_low": "°F",
    "days_high_above": "days",
    "days_high_below": "days",
    "days_low_above": "days",
    "days_low_below": "days",
    "days_precip_above": "days",
}
MUNITS = {
    "total_precip": "mm",
    "gdd": "°C",
    "sdd": "°C",
    "avg_temp": "°C",
    "avg_high": "°C",
    "avg_low": "°C",
    "days_high_above": "days",
    "days_high_below": "days",
    "days_low_above": "days",
    "days_low_below": "days",
    "days_precip_above": "days",
}
PRECISION = {"total_precip": 2}
MDICT = {
    "all": "Annual",
    "custom": "Custom Period (select below)",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "gs": "1 May to 30 Sep",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}
OPT1 = {"diff": "Plot Difference", "p1": "Just Plot Period One Values"}


class Params(AutoplotParams):
    """Request parameters."""

    month: Annotated[
        str,
        SelectArg(
            options=MDICT,
            label="Show Monthly, Annual or Custom Defined Period Averages",
        ),
    ] = "all"
    sday: Annotated[
        date,
        SDayArg(
            label="Inclusive Start Day (select custom period above)",
            default="0101",
        ),
    ]
    eday: Annotated[
        date,
        SDayArg(
            label="Inclusive End Day (select custom period above)",
            default="1231",
        ),
    ]
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
        str, SelectArg(options=PDICT3, label="Which Variable to Plot")
    ] = "total_precip"
    r: Annotated[
        str,
        SelectArg(
            options=PDICT4,
            label="Which Unit System to Use (GDD/SDD always english)",
        ),
    ] = "english"
    threshold: Annotated[
        float, FloatArg(label="Enter threshold (where appropriate)")
    ] = -99
    opt1: Annotated[
        str, SelectArg(options=OPT1, label="Period plotting option")
    ] = "diff"
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
    cmap: Annotated[str, CmapArg(label="Color Ramp:")] = "seismic_r"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def get_data(ctx: Params):
    """Get the data, please."""
    state = ctx.state
    sector = ctx.sector
    threshold = ctx.threshold
    month = ctx.month
    sday: date = ctx.sday
    eday: date = ctx.eday
    p1syear = ctx.p1syear
    p1eyear = ctx.p1eyear
    p1years = p1eyear - p1syear + 1
    p2syear = ctx.p2syear
    p2eyear = ctx.p2eyear
    p2years = p2eyear - p2syear + 1

    datumsql = "year"
    if month != "custom":
        mlimiter = "and month = ANY(:months)" if month != "all" else ""
        months = month2months(month)
    else:
        mlimiter = "and sday >= :sday and sday <= :eday"
        if sday > eday:
            mlimiter = "and (sday >= :sday or sday <= :eday)"
            datumsql = "case when sday >= :sday then year + 1 else year end"
        months = None
    table = "alldata"
    if sector == "state":
        # optimization
        table = f"alldata_{state.lower()}"
    hcol = "high"
    lcol = "low"
    pcol = "precip"
    if ctx.r == "metric":
        hcol = "f2c(high)"
        lcol = "f2c(low)"
        pcol = "precip * 25.4"

    sqlopts = {
        "total_precip": f"sum({pcol})",
        "gdd": "sum(gddxx(50, 86, high, low))",
        "sdd": "sum(case when high > 86 then high - 86 else 0 end)",
        "avg_temp": f"avg(({hcol}+{lcol})/2.0)",
        "avg_high": f"avg({hcol})",
        "avg_low": f"avg({lcol})",
        "days_high_above": (
            f"sum(case when {hcol}::numeric >= :t then 1 else 0 end)"
        ),
        "days_high_below": (
            f"sum(case when {hcol}::numeric < :t then 1 else 0 end)"
        ),
        "days_low_above": (
            f"sum(case when {lcol}::numeric >= :t then 1 else 0 end)"
        ),
        "days_low_below": (
            f"sum(case when {lcol}::numeric < :t then 1 else 0 end)"
        ),
        "days_precip_above": (
            f"sum(case when {pcol}::numeric >= :t then 1 else 0 end)"
        ),
    }

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        WITH period1 as (
            SELECT station, {datumsql} as datum,
            {sqlvar} as {varname}
            from {table} WHERE year >= :syear1 and year <= :eyear1
            {mlimiter} GROUP by station, datum),
        period2 as (
            SELECT station, {datumsql} as datum,
            {sqlvar} as {varname}
            from {table} WHERE year >= :syear2 and year <= :eyear2
            {mlimiter} GROUP by station, datum),
        p1agg as (
            SELECT station,
            avg({varname}) as {varname}, count(*) as count
            from period1 GROUP by station),
        p2agg as (
            SELECT station,
            avg({varname}) as {varname}, count(*) as count
            from period2 GROUP by station),
        agg as (
            SELECT p2.station,
            p2.{varname} as p2_{varname},
            p1.{varname} as p1_{varname}
            from p1agg p1 JOIN p2agg p2 on
            (p1.station = p2.station)
            WHERE p1.count >= :p1years and p2.count >= :p2years)

        SELECT ST_X(geom) as lon, ST_Y(geom) as lat,
        d.* from agg d JOIN stations t ON (d.station = t.id)
        WHERE t.network ~* 'CLIMATE'
        and substr(station, 3, 1) != 'C' and substr(station, 3, 4) != '0000'
        """,
                datumsql=datumsql,
                varname=ctx.var,
                sqlvar=sqlopts[ctx.var],
                table=table,
                mlimiter=mlimiter,
            ),
            conn,
            params={
                "t": threshold,
                "syear1": p1syear,
                "eyear1": p1eyear,
                "months": months,
                "sday": f"{sday:%m%d}",
                "eday": f"{eday:%m%d}",
                "syear2": p2syear,
                "eyear2": p2eyear,
                "p1years": p1years,
                "p2years": p2years,
            },
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df[ctx.var] = df[f"p2_{ctx.var}"] - df[f"p1_{ctx.var}"]
    return df


def geojson(ctx: Params):
    """Handle GeoJSON output."""
    return (get_data(ctx).drop(["lat", "lon"], axis=1)), ctx.var


def plotter(ctx: Params):
    """Go"""
    df = get_data(ctx)
    state = ctx.state
    varname = ctx.var
    sector = ctx.sector
    threshold = ctx.threshold
    opt = ctx.opt
    month = ctx.month
    p1syear = ctx.p1syear
    p1eyear = ctx.p1eyear
    p2syear = ctx.p2syear
    p2eyear = ctx.p2eyear
    opt1 = ctx.opt1

    column = varname
    if month == "custom":
        title = f"({ctx.sday:%-d %b} thru {ctx.eday:%-d %b}) {PDICT3[varname]}"
    else:
        title = f"{MDICT[month]} {PDICT3[varname]}"
    title = title.replace("[Threshold]", f"{threshold:.1f}")
    # this works, for now
    tvar = "total_precip" if "precip" in varname else "avg_high"
    title += f" {(MUNITS if ctx.r == 'metric' else UNITS)[tvar]}"
    if opt1 == "p1":
        column = f"p1_{varname}"
        title = f"{p1syear:.0f}-{p1eyear:.0f} {title}"
    else:
        tt = UNITS[varname] if ctx.r == "english" else MUNITS[varname]
        p1 = (
            f"{p1syear:.0f}-{p1eyear:.0f}"
            if p1syear != p1eyear
            else f"{p1syear:.0f}"
        )
        p2 = (
            f"{p2syear:.0f}-{p2eyear:.0f}"
            if p2syear != p2eyear
            else f"{p2syear:.0f}"
        )
        title = f"{p2} minus {p1} {title} Difference ({tt})"

    # Reindex so that most extreme values are first
    df = df.reindex(df[column].abs().sort_values(ascending=False).index)
    # drop 5% most extreme events, too much?
    df2 = df.iloc[int(len(df.index) * 0.05) :]

    mp = MapPlot(
        apctx=ctx,
        sector=sector,
        state=state,
        axisbg="white",
        title=title,
        subtitle="based on IEM Archives",
        titlefontsize=12,
        nocaption=True,
    )
    if opt1 == "diff":
        # Create 9 levels centered on zero
        abval = df2[column].abs().max()
        levels = centered_bins(abval)
    else:
        levels = [
            round(v, PRECISION.get(varname, 1))
            for v in np.percentile(df2[column].to_numpy(), range(0, 101, 10))
        ]
    if opt in ["both", "contour"]:
        mp.contourf(
            df2["lon"].values,
            df2["lat"].values,
            df2[column].values,
            levels,
            cmap=get_cmap(ctx.cmap),
            units=UNITS[varname] if ctx.r == "english" else MUNITS[varname],
        )
    if sector == "state":
        mp.drawcounties()
    if opt in ["both", "values"]:
        mp.plot_values(
            df2["lon"].values,
            df2["lat"].values,
            df2[column].values,
            fmt=f"%.{PRECISION.get(varname, 1):.0f}f",
            labelbuffer=5,
            zorder=Z_CLIP - 1,  # Lame workaround to keep labels inside mask
        )

    return mp.fig, df.round(2)
