"""climodat days over threshold"""
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
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
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]

    table = "alldata_%s" % (station[:2],)
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
        bs.date(),
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )
    res += ("%s %4s %4s %4s %4s %4s %4s %4s %4s %4s\n" "") % (
        "YEAR",
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

    df = read_sql(
        f"""SELECT year,
       sum(case when low <= -20 THEN 1 ELSE 0 END) as m20,
       sum(case when low <= -10 THEN 1 ELSE 0 END) as m10,
       sum(case when low <=  0 THEN 1 ELSE 0 END) as m0,
       sum(case when low <=  32 THEN 1 ELSE 0 END) as m32,
       sum(case when high >= 50 THEN 1 ELSE 0 END) as e50,
       sum(case when high >= 70 THEN 1 ELSE 0 END) as e70,
       sum(case when high >= 80 THEN 1 ELSE 0 END) as e80,
       sum(case when high >= 93 THEN 1 ELSE 0 END) as e93,
       sum(case when high >= 100 THEN 1 ELSE 0 END) as e100
       from {table} WHERE station = %s GROUP by year ORDER by year ASC
    """,
        pgconn,
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
    plotter(dict())
