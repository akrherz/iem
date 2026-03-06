""".. title:: NLAE Flux Data Export

Return to `API Services </api/#cgi>`_

Example Requests
----------------

Return the flux data for station NSTL11 for 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/nlaeflux.py?station=NSTL11&\
syear=2024&smonth=1&sday=1&eyear=2024&emonth=12&eday=31

"""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import (
    DAY_OF_MONTH_FIELD,
    MONTH_FIELD,
    STATION_LIST_FIELD,
    YEAR_FIELD,
)


class Schema(CGIModel):
    """Request arguments."""

    syear: YEAR_FIELD
    smonth: MONTH_FIELD
    sday: DAY_OF_MONTH_FIELD
    eyear: YEAR_FIELD
    emonth: MONTH_FIELD
    eday: DAY_OF_MONTH_FIELD
    station: STATION_LIST_FIELD


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Handle mod_wsgi request."""
    sts = utc(environ["syear"], environ["smonth"], environ["sday"])
    ets = utc(environ["eyear"], environ["emonth"], environ["eday"])
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
