#!/usr/bin/env python
"""Provide an UTC hour's worth of METARs

 Called from nowhere known at the moment
"""

import cgi
import sys
import datetime

import pytz
from pyiem.util import get_dbconn, ssw


def check_load(cursor):
    """A crude check that aborts this script if there is too much
    demand at the moment"""
    cursor.execute(
        """
    select pid from pg_stat_activity where query ~* 'FETCH'
    and datname = 'asos'"""
    )
    if cursor.rowcount > 9:
        sys.stderr.write(
            ("/cgi-bin/request/metars.py over capacity: %s")
            % (cursor.rowcount,)
        )
        ssw("Content-type: text/plain\n")
        ssw("Status: 503 Service Unavailable\n\n")
        ssw("ERROR: server over capacity, please try later")
        sys.exit(0)


def main():
    """Do Something"""
    pgconn = get_dbconn("asos", user="nobody")
    check_load(pgconn.cursor())
    acursor = pgconn.cursor("streamer")
    ssw("Content-type: text/plain\n\n")
    form = cgi.FieldStorage()
    valid = datetime.datetime.strptime(
        form.getfirst("valid", "2016010100")[:10], "%Y%m%d%H"
    )
    valid = valid.replace(tzinfo=pytz.utc)
    table = "t%s" % (valid.year,)
    acursor.execute(
        """
        SELECT metar from """
        + table
        + """
        WHERE valid >= %s and valid < %s and metar is not null
        ORDER by valid ASC
    """,
        (valid, valid + datetime.timedelta(hours=1)),
    )
    for row in acursor:
        ssw("%s\n" % (row[0].replace("\n", " "),))


if __name__ == "__main__":
    main()
