"""Top 30 24-Hour Precipitation Events.

<a href="/plotting/auto/?q=134">Autoplot 134</a> is a more functional interface
than this legacy "climodat" based one.
"""

from datetime import date
from typing import Annotated

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper

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

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                "SELECT day, precip from alldata WHERE "
                "station = :station and precip is not null "
                "ORDER by precip DESC LIMIT 30"
            ),
            conn,
            params={"station": station},
            index_col=None,
        )

    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        f"# Report Generated: {date.today():%d %b %Y}\n"
        f"# Climate Record: {ctx['_nt'].sts[station]['archive_begin']} "
        f"-> {date.today()}\n"
        f"# Site Information: {ctx.sname}\n"
        "# Contact Information: Daryl Herzmann "
        "akrherz@iastate.edu 515.294.5978\n"
        "# Top 30 single day rainfalls\n"
        " MONTH  DAY  YEAR   AMOUNT\n"
    )

    for _, row in df.iterrows():
        res += (
            f"{row['day'].month:4.0f}{row['day'].day:7.0f}"
            f"{row['day'].year:6.0f}{row['precip']:9.2f}\n"
        )

    return None, df, res
