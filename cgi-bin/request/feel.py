"""FEEL data download"""
# pylint: disable=abstract-class-instantiated
import datetime
from io import BytesIO

import pandas as pd
from paste.request import parse_formvars
from pyiem.util import get_dbconn

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def run(sts, ets, start_response):
    """Get data!"""
    dbconn = get_dbconn("other", user="nobody")
    sql = """SELECT * from feel_data_daily where
    valid >= '%s' and valid < '%s' ORDER by valid ASC""" % (
        sts,
        ets,
    )
    df = pd.read_sql(sql, dbconn)

    sql = """SELECT * from feel_data_hourly where
    valid >= '%s' and valid < '%s' ORDER by valid ASC""" % (
        sts,
        ets,
    )
    df2 = pd.read_sql(sql, dbconn)

    def fmt(val):
        """Lovely hack."""
        return val.strftime("%Y-%m-%d %H:%M")

    df2["valid"] = df2["valid"].apply(fmt)

    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, "Daily Data", index=False)
        df2.to_excel(writer, "Hourly Data", index=False)

    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment;Filename=feel.xlsx"),
    ]
    start_response("200 OK", headers)
    return bio.getvalue()


def application(environ, start_response):
    """Get stuff"""
    form = parse_formvars(environ)
    year1 = int(form.get("year1"))
    year2 = int(form.get("year2"))
    month1 = int(form.get("month1"))
    month2 = int(form.get("month2"))
    day1 = int(form.get("day1"))
    day2 = int(form.get("day2"))

    sts = datetime.datetime(year1, month1, day1)
    ets = datetime.datetime(year2, month2, day2)

    return [run(sts, ets, start_response)]
