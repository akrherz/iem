"""Stress Degree Days."""

from datetime import date
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import PlotDescription
from iemweb.autoplot.params import AutoplotParams


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, report=True, nopng=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station

    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("No Data Found.")
    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        "# Report Generated: %s\n"
        "# Climate Record: %s -> %s\n"
        "# Site Information: [%s] %s\n"
        "# Contact Information: Daryl Herzmann "
        "akrherz@iastate.edu 515.294.5978\n"
    ) % (
        date.today().strftime("%d %b %Y"),
        bs,
        date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )
    res += ("# THESE ARE THE HEAT STRESS VARIABLES FOR STATION #  %s\n") % (
        station,
    )

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT year, month, sum(case when high > 86 then 1 else 0 end)
            as days, sum(case when high > 86 then high - 86 else 0 end) as sdd
            from alldata WHERE station = :station GROUP by year, month
        """),
            conn,
            params={"station": station},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    sdd = df.pivot(index="year", columns="month", values="sdd")
    days = df.pivot(index="year", columns="month", values="days")
    df = sdd.join(days, suffixes=("sdd", "days"))

    res += (
        "             # OF DAYS MAXT >86                     "
        "ACCUMULATED (MAXT - 86 )\n"
        " YEAR   MAY  JUNE  JULY   AUG  SEPT TOTAL      "
        "MAY  JUNE  JULY   AUG  SEPT TOTAL\n"
    )

    yrCnt = 0
    for yr in range(df.index.min(), df.index.max() + 1):
        yrCnt += 1
        res += "%5s" % (yr,)
        total = 0
        for mo in range(5, 10):
            val = df.at[yr, f"{mo}days"]
            if pd.isna(val):
                res += "%6s" % ("M",)
            else:
                res += "%6i" % (val,)
                total += val
        res += "%6i   " % (total,)
        total = 0
        for mo in range(5, 10):
            val = df.at[yr, f"{mo}sdd"]
            if pd.isna(val):
                res += "%6s" % ("M",)
            else:
                res += "%6i" % (val,)
                total += val
        res += "%6i   \n" % (total,)

    res += (
        " **************************************************************"
        "************************\n"
    )

    res += "MEANS"
    tot = 0
    for mo in range(5, 10):
        val = df[f"{mo}days"].mean()
        tot += val
        res += "%6.1f" % (val,)
    res += "%6.1f   " % (tot,)
    tot = 0
    for mo in range(5, 10):
        val = df[f"{mo}sdd"].mean()
        tot += val
        res += "%6.1f" % (val,)
    res += "%6.1f\n" % (tot,)

    return None, df, res
