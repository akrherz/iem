""".. title:: Download PurpleAir Data

Example Requests
----------------

Provide data for 10 August 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/purpleair.py?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z

"""

from io import BytesIO

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def run(environ, start_response):
    """run()"""
    sql = text(
        """
    select * from purpleair where valid >= :sts and valid < :ets
    ORDER by valid asc
    """
    )
    with get_sqlalchemy_conn("other") as conn:
        df = pd.read_sql(
            sql, conn, params={"sts": environ["sts"], "ets": environ["ets"]}
        )
    if environ.get("excel", "no") == "yes":
        df["valid"] = df["valid"].dt.strftime("%Y-%m-%d %H:%M")
        start_response(
            "200 OK",
            [
                ("Content-type", EXL),
                ("Content-Disposition", "attachment; filename=purpleair.xlsx"),
            ],
        )
        bio = BytesIO()
        df.to_excel(bio, index=False, engine="openpyxl")
        return bio.getvalue()
    start_response(
        "200 OK",
        [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=purpleair.csv"),
        ],
    )
    return df.to_csv(None, index=False).encode("ascii")


@iemapp(default_tz="America/Chicago", help=__doc__)
def application(environ, start_response):
    """Go Main Go"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing")

    return [run(environ, start_response)]
