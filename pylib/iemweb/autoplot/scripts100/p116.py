"""
This chart presents monthly cooling degree days
or heating degree days for a 20 year period of your choice.  The 20 year
limit is for plot usability only, the data download has all available
years contained.
"""

from datetime import date
from typing import Annotated

import pandas as pd
import seaborn as sns
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import (
    IntArg,
    PlotDescription,
    SelectArg,
    YearArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {"cdd": "Cooling Degree Days", "hdd": "Heating Degree Days"}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    var: Annotated[str, SelectArg(options=PDICT, label="Select Variable")] = (
        "cdd"
    )
    syear: Annotated[
        int,
        YearArg(
            label="For plotting, year to start 20 years of plot",
            default=lambda: date.today().year - 19,
        ),
    ]
    base: Annotated[int, IntArg(label="CDD/HDD Base Temperature °F")] = 60


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, report=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    varname = ctx.var
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT year, month, sum(precip) as sum_precip,
            avg(high) as avg_high,
            avg(low) as avg_low,
            sum(cdd(high,low,:base)) as cdd,
            sum(cdd(high,low,65)) as cdd65,
            sum(hdd(high,low,:base)) as hdd,
            sum(hdd(high,low,65)) as hdd65,
            sum(case when precip > 0.009 then 1 else 0 end) as rain_days,
            sum(case when snow >= 0.1 then 1 else 0 end) as snow_days
            from alldata WHERE station = :station GROUP by year, month
        """),
            conn,
            params={"station": station, "base": ctx.base},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["monthdate"] = df[["year", "month"]].apply(
        lambda x: date(x.iloc[0], x.iloc[1], 1), axis=1
    )
    df = df.set_index("monthdate")

    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        f"# Report Generated: {date.today():%d %b %Y}\n"
        f"# Climate Record: {ctx['_nt'].sts[station]['archive_begin']} "
        f"-> {date.today()}\n"
        f"# Site Information: {ctx.sname}\n"
        "# Contact Information: Daryl Herzmann "
        "akrherz@iastate.edu 515.294.5978\n"
        f"# THESE ARE THE MONTHLY {PDICT[varname].upper()} (base=65) "
        f"FOR STATION {station}\n"
        "YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    "
        "SEP    OCT    NOV    DEC\n"
    )

    second = (
        f"# THESE ARE THE MONTHLY {PDICT[varname].upper()} "
        f"(base={ctx.base}) "
        f"FOR STATION {station}\n"
        "YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    "
        "SEP    OCT    NOV    DEC\n"
    )
    minyear = df["year"].min()
    maxyear = df["year"].max()
    for yr in range(minyear, maxyear + 1):
        res += f"{yr:4.0f}"
        second += f"{yr:4.0f}"
        for mo in range(1, 13):
            ts = date(yr, mo, 1)
            if ts not in df.index:
                res += f"{'M':>7s}"
                second += f"{'M':>7s}"
                continue
            row = df.loc[ts]
            val = row[f"{varname}65"]
            res += f"{val:7.0f}"
            val = row[f"{varname}"]
            second += f"{val:7.0f}"
        res += "\n"
        second += "\n"

    res += "MEAN"
    second += "MEAN"
    for mo in range(1, 13):
        df2 = df[df["month"] == mo]
        val = df2[f"{varname}65"].mean()
        res += f"{val:7.0f}"
        val = df2[varname].mean()
        second += f"{val:7.0f}"
    res += "\n"
    second += "\n"
    res += second

    y1 = int(ctx.get("syear", 1990))

    title = f"[{station}] {ctx['_nt'].sts[station]['name']} ({y1}-{y1 + 20})"
    fig, ax = figure_axes(
        title=title,
        subtitle=f"{PDICT[varname]} base={ctx.base}°F",
        apctx=ctx,
    )
    filtered = df[(df["year"] >= y1) & (df["year"] <= (y1 + 20))]
    if filtered.empty:
        raise NoDataFound("No data for specified period")
    df2 = filtered[["month", "year", varname]].pivot(
        index="year", columns="month", values=varname
    )
    sns.heatmap(df2, annot=True, fmt=".0f", linewidths=0.5, ax=ax)

    return fig, df, res
