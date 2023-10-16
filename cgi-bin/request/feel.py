"""FEEL data download"""
# pylint: disable=abstract-class-instantiated
from io import BytesIO

import pandas as pd
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def run(sts, ets, start_response):
    """Get data!"""
    with get_sqlalchemy_conn("other") as dbconn:
        sql = """SELECT * from feel_data_daily where
        valid >= %s and valid < %s ORDER by valid ASC"""
        df = pd.read_sql(sql, dbconn, params=(sts, ets))

        sql = """SELECT * from feel_data_hourly where
        valid >= %s and valid < %s ORDER by valid ASC"""
        df2 = pd.read_sql(sql, dbconn, params=(sts, ets))

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


@iemapp()
def application(environ, start_response):
    """Get stuff"""

    return [run(environ["sts"], environ["ets"], start_response)]
