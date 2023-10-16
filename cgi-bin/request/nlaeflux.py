"""Download backend for NLAE Flux Data."""

import pandas as pd
from pyiem.util import get_sqlalchemy_conn, utc
from pyiem.webutil import iemapp
from sqlalchemy import text


@iemapp()
def application(environ, start_response):
    """Handle mod_wsgi request."""
    sts = utc(
        int(environ["syear"]), int(environ["smonth"]), int(environ["sday"])
    )
    ets = utc(
        int(environ["eyear"]), int(environ["emonth"]), int(environ["eday"])
    )
    stations = environ.get("station", [])
    if not isinstance(stations, list):
        stations = [stations]
    if not stations:
        stations = environ.get("station[]", [])
        if not isinstance(stations, list):
            stations = [stations]
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
