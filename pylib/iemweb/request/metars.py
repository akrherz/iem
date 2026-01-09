""".. title:: Request Hour's worth of METARs

Return to `IEM API Mainpage </api/#cgi>`_

Documentation for /cgi-bin/request/metars.py
--------------------------------------------

This is a very simple service that intends on emitting a text file of METARs
that is ammenable to being ingested by other software.  Each METAR is on a
single line and the file is sorted by the observation time.

Example Usage:
--------------

Retrieve all METARs for the hour starting at 00 UTC on 1 January 2016:

https://mesonet.agron.iastate.edu/cgi-bin/request/metars.py\
?valid=2016010100

"""

from datetime import datetime, timedelta, timezone
from io import StringIO

from pydantic import AwareDatetime, Field, field_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.webutil import CGIModel, iemapp

from iemweb import error_log

SIMULTANEOUS_REQUESTS: int = 30


class Schema(CGIModel):
    """Our schema for this request"""

    valid: AwareDatetime = Field(
        ...,
        description=(
            "Hour truncated UTC timestamp to request data for. The "
            "format is `YYYYMMDDHH`."
        ),
    )

    @field_validator("valid", mode="before")
    @classmethod
    def parse_valid(cls, value):
        """Ensure valid is a valid datetime"""
        return datetime.strptime(value, "%Y%m%d%H").replace(
            tzinfo=timezone.utc
        )


def check_load(conn, environ: dict):
    """A crude check that aborts this script if there is too much
    demand at the moment"""
    res = conn.execute(
        sql_helper(
            "select pid from pg_stat_activity where query ~* 'FETCH' "
            "and datname = 'asos'"
        )
    )
    load = len(res.fetchall())
    if load > SIMULTANEOUS_REQUESTS:
        error_log(environ, f"/cgi-bin/request/metars.py over capacity: {load}")
        return False
    return True


@iemapp(schema=Schema, help=__doc__)
def application(environ, start_response):
    """Do Something"""
    with get_sqlalchemy_conn("asos") as conn:
        if not check_load(conn, environ):
            start_response(
                "503 Service Unavailable", [("Content-type", "text/plain")]
            )
            return [b"ERROR: server over capacity, please try later"]
        start_response("200 OK", [("Content-type", "text/plain")])
        valid = environ["valid"]
        res = conn.execute(
            sql_helper("""
            SELECT metar from alldata
            WHERE valid >= :sts and valid < :ets and metar is not null
            ORDER by valid ASC
        """),
            {"sts": valid, "ets": valid + timedelta(hours=1)},
        )
        sio = StringIO()
        for row in res:
            sio.write("%s\n" % (row[0].replace("\n", " "),))
    return [sio.getvalue().encode("ascii", "ignore")]
