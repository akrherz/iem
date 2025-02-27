""".. title:: Hourly Precipitation Data Service

Return to `API Services </api/>`_

Documentation for /cgi-bin/request/hourlyprecip.py
--------------------------------------------------

This service emits hourly precipitation data based on processed METAR
observations by the IEM.

Changelog
---------

- 2024-09-04: Initial update and examples

Example Usage
-------------

Return the hourly precip for Ames, IA for the month of January 2024 with the
station's state and lat/lon included:

https://mesonet.agron.iastate.edu/cgi-bin/request/hourlyprecip.py?\
station=AMW&network=IA_ASOS&sts=2024-01-01T00:00:00Z&ets=2024-02-01T00:00:00Z\
&st=1&lalo=1

"""

from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, Field, field_validator
from pyiem.database import get_dbconn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp


class Schema(CGIModel):
    """See how we are called."""

    ets: AwareDatetime = Field(
        None, description="The end of the requested interval."
    )
    lalo: bool = Field(False, description="Include the lat/lon in the output.")
    network: str = Field(
        "IA_ASOS",
        description="The network to request data for.",
        max_length=12,
    )
    st: bool = Field(False, description="Include the state in the output.")
    station: ListOrCSVType = Field(
        [], description="The station(s) to request data for."
    )
    sts: AwareDatetime = Field(
        None, description="The start of the requested interval."
    )
    tz: str = Field(
        "America/Chicago",
        description=(
            "The timezone to present the data in and for requested interval."
        ),
    )
    year1: int = Field(None, description="The start year, when sts is unset.")
    month1: int = Field(
        None, description="The start month, when sts is unset."
    )
    day1: int = Field(None, description="The start day, when sts is unset.")
    year2: int = Field(None, description="The end year, when ets is unset.")
    month2: int = Field(None, description="The end month, when ets is unset.")
    day2: int = Field(None, description="The end day, when ets is unset.")

    @field_validator("tz", mode="after")
    @classmethod
    def validate_tz(cls, value):
        """Ensure the timezone is valid."""
        try:
            ZoneInfo(value)
        except Exception as exp:
            raise ValueError("Invalid timezone") from exp
        return value


def get_data(network, environ, tzinfo):
    """Go fetch data please"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    res = "station,network,valid,precip_in"
    sql = ""
    if environ["lalo"]:
        res += ",lat,lon"
        sql += " , st_y(geom) as lat, st_x(geom) as lon "
    if environ["st"]:
        res += ",st"
        sql += ", state "
    res += "\n"
    cursor.execute(
        f"""
        SELECT id, t.network, valid, phour {sql}
        from hourly h JOIN stations t on
        (h.iemid = t.iemid) WHERE
        valid >= %s and valid < %s and t.network = %s and t.id = ANY(%s)
        ORDER by valid ASC
        """,
        (environ["sts"], environ["ets"], network, environ["station"]),
    )
    for row in cursor:
        res += (
            f"{row[0]},{row[1]},{row[2].astimezone(tzinfo):%Y-%m-%d %H:%M},"
            f"{','.join([str(x) for x in row[3:]])}\n"
        )

    return res.encode("ascii", "ignore")


@iemapp(help=__doc__, default_tz="America/Chicago", schema=Schema)
def application(environ, start_response):
    """run rabbit run"""
    tzinfo = ZoneInfo(environ["tz"])
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing start or end time.")
    if not environ["station"]:
        raise IncompleteWebRequest("No station= was specified.")
    start_response("200 OK", [("Content-type", "text/plain")])
    network = environ["network"]
    return [get_data(network, environ, tzinfo)]
