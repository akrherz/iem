"""Provide an UTC hour's worth of METARs

 Called from nowhere known at the moment
"""
from io import StringIO
import sys
import datetime

import pytz
from paste.request import parse_formvars
from pyiem.util import get_dbconn


def check_load(cursor):
    """A crude check that aborts this script if there is too much
    demand at the moment"""
    cursor.execute(
        "select pid from pg_stat_activity where query ~* 'FETCH' "
        "and datname = 'asos'"
    )
    if cursor.rowcount > 9:
        sys.stderr.write(
            f"/cgi-bin/request/metars.py over capacity: {cursor.rowcount}\n"
        )
        return False
    return True


def application(environ, start_response):
    """Do Something"""
    pgconn = get_dbconn("asos")
    if not check_load(pgconn.cursor()):
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        return [b"ERROR: server over capacity, please try later"]
    acursor = pgconn.cursor("streamer")
    start_response("200 OK", [("Content-type", "text/plain")])
    form = parse_formvars(environ)
    valid = datetime.datetime.strptime(
        form.get("valid", "2016010100")[:10], "%Y%m%d%H"
    )
    valid = valid.replace(tzinfo=pytz.UTC)
    acursor.execute(
        """
        SELECT metar from alldata
        WHERE valid >= %s and valid < %s and metar is not null
        ORDER by valid ASC
    """,
        (valid, valid + datetime.timedelta(hours=1)),
    )
    sio = StringIO()
    for row in acursor:
        sio.write("%s\n" % (row[0].replace("\n", " "),))
    return [sio.getvalue().encode("ascii", "ignore")]
