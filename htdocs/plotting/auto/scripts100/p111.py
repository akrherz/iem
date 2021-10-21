"""Climodat"""
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
    df = read_sql(
        f"SELECT day, precip from {table} WHERE station = %s and "
        "precip is not null ORDER by precip DESC LIMIT 30",
        pgconn,
        params=(station,),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found.")

    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# Top 30 single day rainfalls
 MONTH  DAY  YEAR   AMOUNT
""" % (
        datetime.date.today().strftime("%d %b %Y"),
        ctx["_nt"].sts[station]["archive_begin"].date(),
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )

    for _, row in df.iterrows():
        res += "%4i%7i%6i%9.2f\n" % (
            row["day"].month,
            row["day"].day,
            row["day"].year,
            row["precip"],
        )

    return None, df, res


if __name__ == "__main__":
    plotter(dict())
