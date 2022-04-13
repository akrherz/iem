"""Days per year"""
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
    station = ctx["station"].upper()

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"SELECT year, count(low) from alldata_{station[:2]} "
            "WHERE station = %s and low >= 32 and year < %s "
            "GROUP by year ORDER by year ASC",
            conn,
            params=(station, datetime.date.today().year),
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
# OF DAYS EACH YEAR WHERE MIN >=32 F
""" % (
        datetime.date.today().strftime("%d %b %Y"),
        ctx["_nt"].sts[station]["archive_begin"],
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )

    for _, row in df.iterrows():
        res += "%s %3i\n" % (row["year"], row["count"])

    res += "MEAN %3i\n" % (df["count"].mean(),)

    return None, df, res


if __name__ == "__main__":
    plotter({})
