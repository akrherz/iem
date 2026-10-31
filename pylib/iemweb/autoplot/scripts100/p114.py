"""Days per year"""

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
    station = ctx.station.upper()

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                "SELECT year, count(low) from alldata "
                "WHERE station = :station and low >= 32 and year < :year "
                "GROUP by year ORDER by year ASC"
            ),
            conn,
            params={"station": station, "year": date.today().year},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# OF DAYS EACH YEAR WHERE MIN >=32 F
""" % (
        date.today().strftime("%d %b %Y"),
        ctx["_nt"].sts[station]["archive_begin"],
        date.today(),
        ctx.sname,
    )

    for _, row in df.iterrows():
        res += "%s %3i\n" % (row["year"], row["count"])

    res += "MEAN %3i\n" % (df["count"].mean(),)

    return None, df, res
