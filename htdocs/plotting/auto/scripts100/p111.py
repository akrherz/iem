"""Climodat"""
import datetime

import pandas as pd
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["report"] = True
    desc["description"] = """ """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        )
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"SELECT day, precip from alldata_{station[:2]} WHERE "
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


if __name__ == "__main__":
    plotter({})
