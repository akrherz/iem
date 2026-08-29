""".. title:: SMOS Request

Return to `API Services </api/#cgi>`_

Documentation for /cgi-bin/request/smos.py
------------------------------------------

This allows downloading of the IEM archived SMOS data for the midwest.

"""

from typing import Annotated

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest, NoDataFound
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD,
    LATITUDE_FIELD,
    LONGITUDE_FIELD,
    MINUTE_FIELD,
    MONTH_FIELD_OPTIONAL,
    YEAR_FIELD_OPTIONAL,
)


class Schema(CGIModel):
    """Our schema for this request"""

    lat: LATITUDE_FIELD
    lon: LONGITUDE_FIELD
    ets: Annotated[
        AwareDatetime | None,
        Field(
            description=(
                "End timestamp with timezone included to request data for."
            ),
        ),
    ] = None
    sts: Annotated[
        AwareDatetime | None,
        Field(
            description=(
                "Start timestamp with timezone included to request data for."
            ),
        ),
    ] = None
    year1: YEAR_FIELD_OPTIONAL = None
    year2: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD = 0
    hour2: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    minute2: MINUTE_FIELD = 0


@iemapp(schema=Schema, help=__doc__)
def application(environ, start_response):
    """Do Something"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Both start and end time must be provided!")

    with get_sqlalchemy_conn("smos") as conn:
        res = conn.execute(
            sql_helper("""
    select idx, st_distance(geom, ST_Point(:lon, :lat, 4326)) as dist
    from grid ORDER by dist ASC LIMIT 1
                       """),
            {"lon": environ["lon"], "lat": environ["lat"]},
        )
        row = res.first()
        if row is None or row[1] > 1:
            raise NoDataFound("Point too far away from our grid!")
        idx = row[0]

        res = conn.execute(
            sql_helper(
                """
    SELECT valid at time zone 'UTC',
    case when soil_moisture is null then 'M' else soil_moisture::text end
    as sm,
    case when optical_depth is null then 'M' else optical_depth::text end
    as od from data where grid_idx = :idx and valid >= :sts and
    valid <= :ets ORDER by valid ASC
"""
            ),
            {
                "idx": idx,
                "sts": environ["sts"],
                "ets": environ["ets"],
            },
        )

        start_response("200 OK", [("Content-type", "text/plain")])
        data = "Timestamp,Longitude,Latitude,Soil_Moisture,Optical_Depth\n"
        for row in res:
            data += (
                f"{row[0]},"
                f"{environ['lon']},{environ['lat']},"
                f"{row[1]},{row[2]}\n"
            )
        return [data.encode("ascii")]
