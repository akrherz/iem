""".. title:: NLAE Flux Data Export

Return to `API Services </api/#cgi>`_

"""

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """Request arguments."""

    syear: int = Field(..., description="Start Year")
    smonth: int = Field(..., description="Start Month")
    sday: int = Field(..., description="Start Day")
    eyear: int = Field(..., description="End Year")
    emonth: int = Field(..., description="End Month")
    eday: int = Field(..., description="End Day")
    station: ListOrCSVType = Field(..., description="Station Identifier")


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Handle mod_wsgi request."""
    sts = utc(
        int(environ["syear"]), int(environ["smonth"]), int(environ["sday"])
    )
    ets = utc(
        int(environ["eyear"]), int(environ["emonth"]), int(environ["eday"])
    )
    stations = environ["station"]
    with get_sqlalchemy_conn("other") as conn:
        df = pd.read_sql(
            text(
                """
            select *, valid at time zone 'UTC' as utc_valid
            from flux_data where valid >= :sts and valid < :ets
            and station = ANY(:stations)
            """
            ),
            conn,
            params={"stations": stations, "sts": sts, "ets": ets},
            parse_dates=["utc_valid"],
        )
    df["valid"] = df["utc_valid"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.drop(columns=["utc_valid"])
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", "attachment; filename=fluxdata.txt"),
    ]
    start_response("200 OK", headers)
    return [df.to_csv(index=False).encode("ascii")]
