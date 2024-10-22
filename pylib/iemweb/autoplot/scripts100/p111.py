"""Top 30 24-Hour Precipitation Events."""

import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

from iemweb.autoplot import ARG_STATION


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {
        "description": __doc__,
        "data": True,
        "report": True,
        "nopng": True,
    }
    desc["arguments"] = [
        ARG_STATION,
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            "SELECT day, precip from alldata WHERE "
            "station = %s and precip is not null "
            "ORDER by precip DESC LIMIT 30",
            conn,
            params=(station,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        f"# Report Generated: {datetime.date.today():%d %b %Y}\n"
        f"# Climate Record: {ctx['_nt'].sts[station]['archive_begin']} "
        f"-> {datetime.date.today()}\n"
        f"# Site Information: {ctx['_sname']}\n"
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
