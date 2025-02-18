""".. title:: SMOS Request

Return to `API Services </api/#cgi>`_

Documentation for /cgi-bin/request/smos.py
------------------------------------------

This allows downloading of the IEM archived SMOS data for the midwest.

Examples:
---------

Download all 2024 data for a point near Ames

https://mesonet.agron.iastate.edu/cgi-bin/request/smos.py?\
sts=2023-01-01T00:00Z&ets=2024-01-01T00:00Z&lat=42.0&lon=-93.0

"""

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest, NoDataFound
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """Our schema for this request"""

    lat: float = Field(
        ...,
        description="Latitude of point to request data for.",
        le=90,
        ge=-90,
    )
    lon: float = Field(
        ...,
        description="West longitude of point to request data for.",
        le=180,
        ge=-180,
    )
    ets: AwareDatetime = Field(
        None,
        description=(
            "End timestamp with timezone included to request data for."
        ),
    )
    sts: AwareDatetime = Field(
        None,
        description=(
            "Start timestamp with timezone included to request data for."
        ),
    )
    year1: int = Field(
        None,
        description=(
            "Year to request data for, this is an alternative to sts/ets."
        ),
    )
    year2: int = Field(
        None,
        description=(
            "Year to request data for, this is an alternative to sts/ets."
        ),
    )
    month1: int = Field(
        None,
        description=(
            "Month to request data for, this is an alternative to sts/ets."
        ),
    )
    month2: int = Field(
        None,
        description=(
            "Month to request data for, this is an alternative to sts/ets."
        ),
    )
    day1: int = Field(
        None,
        description=(
            "Day to request data for, this is an alternative to sts/ets."
        ),
    )
    day2: int = Field(
        None,
        description=(
            "Day to request data for, this is an alternative to sts/ets."
        ),
    )
    hour1: int = Field(0, description="Hour to request data for.")
    hour2: int = Field(0, description="Hour to request data for.")
    minute1: int = Field(0, description="Minute to request data for.")
    minute2: int = Field(0, description="Minute to request data for.")


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
