"""Provide an UTC hour's worth of METARs

 Called from nowhere known at the moment
"""
import datetime
import sys
from io import StringIO
from zoneinfo import ZoneInfo

from pyiem.webutil import iemapp


def check_load(cursor):
    """A crude check that aborts this script if there is too much
    demand at the moment"""
    cursor.execute(
        "select pid from pg_stat_activity where query ~* 'FETCH' "
        "and datname = 'asos'"
    )
    if len(cursor.fetchall()) > 9:
        sys.stderr.write(
            f"/cgi-bin/request/metars.py over capacity: {cursor.rowcount}\n"
        )
        return False
    return True


@iemapp(iemdb="asos", iemdb_cursorname="streamer")
def application(environ, start_response):
    """Do Something"""
    cursor = environ["iemdb.asos.cursor"]
    if not check_load(cursor):
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        return [b"ERROR: server over capacity, please try later"]
    start_response("200 OK", [("Content-type", "text/plain")])
    valid = datetime.datetime.strptime(
        environ.get("valid", "2016010100")[:10], "%Y%m%d%H"
    )
    valid = valid.replace(tzinfo=ZoneInfo("UTC"))
    cursor.execute(
        """
        SELECT metar from alldata
        WHERE valid >= %s and valid < %s and metar is not null
        ORDER by valid ASC
    """,
        (valid, valid + datetime.timedelta(hours=1)),
    )
    sio = StringIO()
    for row in cursor:
        sio.write("%s\n" % (row["metar"].replace("\n", " "),))
    return [sio.getvalue().encode("ascii", "ignore")]
