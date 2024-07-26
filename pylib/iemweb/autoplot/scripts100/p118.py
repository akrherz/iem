"""precip days per month"""

import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

from iemweb.autoplot import ARG_STATION

PDICT = {"precip_days": "Precipitation Days", "snow_days": "Snowfall Days"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "report": True}
    desc["arguments"] = [
        ARG_STATION,
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
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT year, month,
            sum(case when precip > 0.009 then 1 else 0 end) as precip_days,
            sum(case when snow > 0.009 then 1 else 0 end) as snow_days
            from alldata WHERE station = %s
            GROUP by year, month
        """,
            conn,
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
        ctx["_nt"].sts[station]["archive_begin"],
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
