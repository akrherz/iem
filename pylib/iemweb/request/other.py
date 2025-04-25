""".. title:: IEM Request Handler for Other Data

Return to `API Services </api/#cgi>`_

Changelog
---------

- 2025-01-03: Use pydantic for request validation

Example Requests
----------------

Provide data for 1 Jan 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/other.py?\
station=DSM&sts=2024-01-01&ets=2024-01-02

"""

from datetime import date
from io import StringIO

from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    station: str = Field(
        ..., description="Station Identifier", max_length=10, min_length=3
    )
    ets: date = Field(None, description="End Time")
    sts: date = Field(None, description="Start Time")
    year1: int = Field(None, description="Year 1")
    month1: int = Field(None, description="Month 1")
    day1: int = Field(None, description="Day 1")
    year2: int = Field(None, description="Year 2")
    month2: int = Field(None, description="Month 2")
    day2: int = Field(None, description="Day 2")


def fetcher(station: str, sts: date, ets: date):
    """
    Fetch the data
    """
    cols = [
        "station",
        "valid",
        "tmpf",
        "dwpf",
        "drct",
        "sknt",
        "gust",
        "relh",
        "alti",
        "pcpncnt",
        "pday",
        "pmonth",
        "srad",
    ]

    pgconn, cursor = get_dbconnc("other")
    cursor.execute(
        """
    SELECT * from alldata where station = %s and valid between %s and %s
    ORDER by valid ASC
    """,
        (station, sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")),
    )

    sio = StringIO()
    sio.write(
        "station,valid_CST_CDT,air_tmp_F,dew_point_F,"
        "wind_dir_deg,wind_sped_kts,wind_gust_kts,relh_%,"
        "alti_in,pcpncnt_in,precip_day_in,precip_month_in,"
        "solar_rad_wms\n"
    )

    for row in cursor:
        sio.write(",".join(f"{row[col]}" for col in cols))
        sio.write("\n")
    pgconn.close()
    return sio.getvalue().encode("ascii")


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """
    Do something!
    """
    station = environ["station"]
    start_response("200 OK", [("Content-type", "text/plain")])
    return [fetcher(station, environ["sts"], environ["ets"])]
