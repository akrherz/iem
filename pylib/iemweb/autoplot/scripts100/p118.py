"""precip days per month"""

from datetime import date
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import PlotDescription, SelectArg
from iemweb.autoplot.params import AutoplotParams

PDICT = {"precip_days": "Precipitation Days", "snow_days": "Snowfall Days"}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    var: Annotated[str, SelectArg(options=PDICT, label="Select Variable")] = (
        "precip_days"
    )


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True, report=True, nopng=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    varname = ctx.var

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT year, month,
            sum(case when precip > 0.009 then 1 else 0 end) as precip_days,
            sum(case when snow > 0.009 then 1 else 0 end) as snow_days
            from alldata WHERE station = :station
            GROUP by year, month
        """),
            conn,
            params={"station": station},
            index_col=["year", "month"],
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# NUMBER OF DAYS WITH %s PER MONTH PER YEAR
# Days with a trace accumulation are not included
YEAR   JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC ANN
""" % (
        date.today().strftime("%d %b %Y"),
        ctx["_nt"].sts[station]["archive_begin"],
        date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
        "PRECIPITATION" if varname == "precip_days" else "SNOW FALL",
    )

    for year in df.index.levels[0]:
        res += "%4i  " % (year,)
        total = 0
        for month in df.index.levels[1]:
            try:
                val = df.at[(year, month), varname]
                total += val
                res += " %3i" % (val,)
            except Exception:
                res += "    "
        res += " %3i\n" % (total,)
    return None, df, res
