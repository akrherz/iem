"""To be written."""

import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.util import get_autoplot_context


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "report": True}
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
        datetime.date.today().strftime("%d %b %Y"),
        bs,
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )
    res += ("# THESE ARE THE HEAT STRESS VARIABLES FOR STATION #  %s\n") % (
        station,
    )

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT year, month, sum(case when high > 86 then 1 else 0 end)
            as days, sum(case when high > 86 then high - 86 else 0 end) as sdd
            from alldata WHERE station = %s GROUP by year, month
        """,
            conn,
            params=(station,),
            index_col=None,
        )
    sdd = df.pivot(index="year", columns="month", values="sdd")
    days = df.pivot(index="year", columns="month", values="days")
    df = sdd.join(days, lsuffix="sdd", rsuffix="days")

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
            val = df.at[yr, "%sdays" % (mo,)]
            if np.isnan(val):
                res += "%6s" % ("M",)
            else:
                res += "%6i" % (val,)
                total += val
        res += "%6i   " % (total,)
        total = 0
        for mo in range(5, 10):
            val = df.at[yr, "%ssdd" % (mo,)]
            if np.isnan(val):
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
        val = df["%sdays" % (mo,)].mean()
        tot += val
        res += "%6.1f" % (val,)
    res += "%6.1f   " % (tot,)
    tot = 0
    for mo in range(5, 10):
        val = df["%ssdd" % (mo,)].mean()
        tot += val
        res += "%6.1f" % (val,)
    res += "%6.1f\n" % (tot,)

    return None, df, res


if __name__ == "__main__":
    plotter({})
