"""
Download NASS Iowa data.
"""
from io import BytesIO

import pandas as pd
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@iemapp()
def application(_environ, start_response):
    """Go Main Go"""
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=nass_iowa.xlsx"),
    ]
    start_response("200 OK", headers)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            "SELECT * from nass_iowa ORDER by valid ASC",
            conn,
            parse_dates="load_time",
        )
    df["load_time"] = df["load_time"].dt.strftime("%Y-%m-%d")
    bio = BytesIO()
    df.to_excel(bio, index=False)
    return [bio.getvalue()]
