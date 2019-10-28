"""precip days per month"""
import datetime
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"precip_days": "Precipitation Days", "snow_days": "Snowfall Days"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
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
        ),
        dict(
            type="select",
            name="var",
            options=PDICT,
            default="precip_days",
            label="Select Variable",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]

    table = "alldata_%s" % (station[:2],)
    df = read_sql(
        """
        SELECT year, month,
        sum(case when precip >= 0.01 then 1 else 0 end) as precip_days,
        sum(case when snow >= 0.01 then 1 else 0 end) as snow_days
        from """
        + table
        + """ WHERE station = %s
        GROUP by year, month
    """,
        pgconn,
        params=(station,),
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
        datetime.date.today().strftime("%d %b %Y"),
        ctx["_nt"].sts[station]["archive_begin"].date(),
        datetime.date.today(),
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


if __name__ == "__main__":
    plotter(dict())
