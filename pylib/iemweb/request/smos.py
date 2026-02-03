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


class Schema(CGIModel):
    """Our schema for this request"""

    lat: Annotated[
        float,
        Field(
            ...,
            description="Latitude of point to request data for.",
            le=90,
            ge=-90,
        ),
    ]
    lon: Annotated[
        float,
        Field(
            ...,
            description="West longitude of point to request data for.",
            le=180,
            ge=-180,
        ),
    ]
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
    year1: Annotated[
        int | None,
        Field(
            description=(
                "Year to request data for, this is an alternative to sts/ets."
            ),
        ),
    ] = None
    year2: Annotated[
        int | None,
        Field(
            description=(
                "Year to request data for, this is an alternative to sts/ets."
            ),
        ),
    ] = None
    month1: Annotated[
        int | None,
        Field(
            description=(
                "Month to request data for, this is an alternative to sts/ets."
            ),
        ),
    ] = None
    month2: Annotated[
        int | None,
        Field(
            description=(
                "Month to request data for, this is an alternative to sts/ets."
            ),
        ),
    ] = None
    day1: Annotated[
        int | None,
        Field(
            description=(
                "Day to request data for, this is an alternative to sts/ets."
            ),
        ),
    ] = None
    day2: Annotated[
        int | None,
        Field(
            description=(
                "Day to request data for, this is an alternative to sts/ets."
            ),
        ),
    ] = None
    hour1: Annotated[
        int,
        Field(
            description="Hour to request data for.",
            ge=0,
            le=23,
        ),
    ] = 0
    hour2: Annotated[
        int,
        Field(
            description="Hour to request data for.",
            ge=0,
            le=23,
        ),
    ] = 0
    minute1: Annotated[
        int,
        Field(
            description="Minute to request data for.",
            ge=0,
            le=59,
        ),
    ] = 0
    minute2: Annotated[
        int,
        Field(
            description="Minute to request data for.",
            ge=0,
            le=59,
        ),
    ] = 0


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
