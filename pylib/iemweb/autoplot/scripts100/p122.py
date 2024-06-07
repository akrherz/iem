"""
A simple accounting of the number of days with a low temperature below the
given threshold or above the given threshold by year.
"""

import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn


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
        raise NoDataFound("No data Found.")
    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        "# Report Generated: %s\n"
        "# Climate Record: %s -> %s\n"
        "# Site Information: [%s] %s\n"
        "# Contact Information: Daryl Herzmann akrherz@iastate.edu "
        "515.294.5978\n"
        "# Number of days exceeding given temperature thresholds\n"
        "# -20, -10, 0, 32 are days with low temperature at or below value\n"
        "# 50, 70, 80, 93, 100 are days with high temperature at or "
        "above value\n"
    ) % (
        datetime.date.today().strftime("%d %b %Y"),
        bs,
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )
    res += ("YEAR %4s %4s %4s %4s %4s %4s %4s %4s %4s\n") % (
        -20,
        -10,
        0,
        32,
        50,
        70,
        80,
        93,
        100,
    )
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """SELECT year,
        sum(case when low <= -20 THEN 1 ELSE 0 END) as m20,
        sum(case when low <= -10 THEN 1 ELSE 0 END) as m10,
        sum(case when low <=  0 THEN 1 ELSE 0 END) as m0,
        sum(case when low <=  32 THEN 1 ELSE 0 END) as m32,
        sum(case when high >= 50 THEN 1 ELSE 0 END) as e50,
        sum(case when high >= 70 THEN 1 ELSE 0 END) as e70,
        sum(case when high >= 80 THEN 1 ELSE 0 END) as e80,
        sum(case when high >= 93 THEN 1 ELSE 0 END) as e93,
        sum(case when high >= 100 THEN 1 ELSE 0 END) as e100
        from alldata
        WHERE station = %s GROUP by year ORDER by year ASC
        """,
            conn,
            params=(station,),
            index_col=None,
        )

    for _, row in df.iterrows():
        res += (
            "%(year)4i %(m20)4i %(m10)4i %(m0)4i %(m32)4i %(e50)4i "
            "%(e70)4i %(e80)4i %(e93)4i %(e100)4i\n"
        ) % row

    return None, df, res


if __name__ == "__main__":
    plotter({})
