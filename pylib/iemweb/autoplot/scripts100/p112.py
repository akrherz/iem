"""
This application totals growing degree days by
month and year.
"""

from datetime import date

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound

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
        dict(
            type="int",
            name="base",
            default="52",
            label="Growing Degree Day Base (F)",
        ),
        dict(
            type="int",
            name="ceil",
            default="86",
            label="Growing Degree Day Ceiling (F)",
        ),
    ]
    return desc


def modMonth(
    stationID, db, monthly, mo1, mo2, mt1, mt2, ctx, gddbase, gddceil
):
    """modMonth."""
    res = (
        "\n               %-12s                %-12s\n"
        "     ****************************  ***************************\n"
        " YEAR  40-86  48-86  50-86  %.0f-%.0f"
        "   40-86  48-86  50-86  %.0f-%.0f\n"
        "     ****************************  *************************** \n"
    ) % (mt1, mt2, gddbase, gddceil, gddbase, gddceil)
    ab = ctx["_nt"].sts[stationID]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    s = ab.year
    e = date(date.today().year + 1, 1, 1)
    for year in range(s, e.year):
        now = date(year, 1, 1)
        m1 = now.replace(month=mo1)
        m2 = now.replace(month=mo2)
        if m1 >= e or m1 not in db:
            db[m1] = {"40": "M", "48": "M", "50": "M", "XX": "M"}
        if m2 >= e or m2 not in db:
            db[m2] = {"40": "M", "48": "M", "50": "M", "XX": "M"}
        res += ("%5i%7s%7s%7s%7s%7s%7s%7s%7s\n") % (
            now.year,
            db[m1]["40"],
            db[m1]["48"],
            db[m1]["50"],
            db[m1]["XX"],
            db[m2]["40"],
            db[m2]["48"],
            db[m2]["50"],
            db[m2]["XX"],
        )

    res += "     ****************************  ****************************\n"
    res += (" MEAN%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f\n") % (
        np.average(monthly[mo1]["40"]),
        np.average(monthly[mo1]["48"]),
        np.average(monthly[mo1]["50"]),
        np.average(monthly[mo1]["XX"]),
        np.average(monthly[mo2]["40"]),
        np.average(monthly[mo2]["48"]),
        np.average(monthly[mo2]["50"]),
        np.average(monthly[mo2]["XX"]),
    )
    res += (" STDV%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f\n") % (
        np.std(monthly[mo1]["40"]),
        np.std(monthly[mo1]["48"]),
        np.std(monthly[mo1]["50"]),
        np.std(monthly[mo1]["XX"]),
        np.std(monthly[mo2]["40"]),
        np.std(monthly[mo2]["48"]),
        np.std(monthly[mo2]["50"]),
        np.std(monthly[mo2]["XX"]),
    )
    return res


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    gddbase = ctx["base"]
    gddceil = ctx["ceil"]
    varname = f"gdd{gddbase}{gddceil}"

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        SELECT year, month, sum(precip) as sum_precip,
        avg(high) as avg_high,
        avg(low) as avg_low,
        sum(cdd(high,low,60)) as cdd60,
        sum(cdd(high,low,65)) as cdd65,
        sum(hdd(high,low,60)) as hdd60,
        sum(hdd(high,low,65)) as hdd65,
        sum(case when precip > 0.009 then 1 else 0 end) as rain_days,
        sum(case when snow >= 0.1 then 1 else 0 end) as snow_days,
        sum(gddxx(40,86,high,low)) as gdd40,
        sum(gddxx(48,86,high,low)) as gdd48,
        sum(gddxx(50,86,high,low)) as gdd50,
        sum(gddxx(:gddbase, :gddceil, high, low)) as {varname}
        from alldata WHERE station = :station GROUP by year, month
        """,
                varname=varname,
            ),
            conn,
            params={
                "station": station,
                "gddbase": gddbase,
                "gddceil": gddceil,
            },
            index_col=None,
        )

    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("No Data Found.")
    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
""" % (
        date.today().strftime("%d %b %Y"),
        bs,
        date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )
    res += ("# GROWING DEGREE DAYS FOR 4 BASE TEMPS FOR STATION ID %s\n") % (
        station,
    )

    monthly = [{"40": [], "48": [], "50": [], "XX": []}] * 13

    db = {}
    for _, row in df.iterrows():
        ts = date(int(row["year"]), int(row["month"]), 1)
        db[ts] = {
            "40": float(row["gdd40"]),
            "48": float(row["gdd48"]),
            "50": float(row["gdd50"]),
            "XX": float(row[varname]),
        }
        monthly[ts.month]["40"].append(float(row["gdd40"]))
        monthly[ts.month]["48"].append(float(row["gdd48"]))
        monthly[ts.month]["50"].append(float(row["gdd50"]))
        monthly[ts.month]["XX"].append(float(row[varname]))

    res += modMonth(
        station,
        db,
        monthly,
        1,
        2,
        "JANUARY",
        "FEBRUARY",
        ctx,
        gddbase,
        gddceil,
    )
    res += modMonth(
        station, db, monthly, 3, 4, "MARCH", "APRIL", ctx, gddbase, gddceil
    )
    res += modMonth(
        station, db, monthly, 5, 6, "MAY", "JUNE", ctx, gddbase, gddceil
    )
    res += modMonth(
        station, db, monthly, 7, 8, "JULY", "AUGUST", ctx, gddbase, gddceil
    )
    res += modMonth(
        station,
        db,
        monthly,
        9,
        10,
        "SEPTEMBER",
        "OCTOBER",
        ctx,
        gddbase,
        gddceil,
    )
    res += modMonth(
        station,
        db,
        monthly,
        11,
        12,
        "NOVEMBER",
        "DECEMBER",
        ctx,
        gddbase,
        gddceil,
    )

    return None, df, res
