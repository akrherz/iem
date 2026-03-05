""".. title:: NLAE Flux Data Export

Return to `API Services </api/#cgi>`_

Example Requests
----------------

Return the flux data for station NSTL11 for 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/nlaeflux.py?station=NSTL11&\
syear=2024&smonth=1&sday=1&eyear=2024&emonth=12&eday=31

"""

import re
from typing import Annotated

import pandas as pd
from pydantic import Field, field_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

from iemweb.fields import DAY_OF_MONTH_FIELD, MONTH_FIELD, YEAR_FIELD

STATION_RE = re.compile(r"^[A-Z0-9_]{3,12}$")


class Schema(CGIModel):
    """Request arguments."""

    syear: YEAR_FIELD
    smonth: MONTH_FIELD
    sday: DAY_OF_MONTH_FIELD
    eyear: YEAR_FIELD
    emonth: MONTH_FIELD
    eday: DAY_OF_MONTH_FIELD
    station: Annotated[ListOrCSVType, Field(description="Station Identifier")]

    @field_validator("station", mode="before")
    def _fix_station(cls, v):
        """Fix up station."""
        if isinstance(v, str):
            v = [v]
        for item in v:
            if not STATION_RE.match(item):
                raise ValueError(f"Invalid station: {item}")

        return v


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
            sql_helper(
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
