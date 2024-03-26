""".. title:: Download NASS Iowa Data

Documentation for /cgi-bin/request/nass_iowa.py
-----------------------------------------------

This service provides a download of the NASS Iowa data that is ingested into
the IEM database.  The data is available in Excel format.  There are no options
to this service at this time.

Example Usage
~~~~~~~~~~~~~

   https://mesonet.agron.iastate.edu/cgi-bin/request/nass_iowa.py

"""

from io import BytesIO

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@iemapp(help=__doc__)
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
