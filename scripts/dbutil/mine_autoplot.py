"""Database found apache log entries of autoplot generation timing

Run from RUN_10_AFTER.sh
"""
from __future__ import print_function
import datetime
import re

from pyiem.util import get_dbconn

LOGRE = re.compile(r"Autoplot\[\s*(\d+)\] Timing:\s*(\d+\.\d+)s Key: ([^\s]*)")
LOGFN = "/var/log/mesonet/error_log"


def get_dbendts(cursor):
    """Figure out when we have data until"""
    cursor.execute("""SELECT max(valid) from autoplot_timing""")
    ts = cursor.fetchone()[0]
    if ts is None:
        ts = datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        ts = ts.replace(tzinfo=None)
    return ts


def find_and_save(cursor, dbendts):
    """Do work please"""
    now = datetime.datetime.now()
    thisyear = now.year
    inserts = 0
    for line in open(LOGFN, "rb"):
        line = line.decode("utf-8", "ignore")
        tokens = LOGRE.findall(line)
        if len(tokens) != 1:
            continue
        (appid, timing, uri) = tokens[0]
        valid = datetime.datetime.strptime(
            "%s %s" % (thisyear, line[:15]), "%Y %b %d %H:%M:%S"
        )
        if valid > now or valid <= dbendts:
            continue
        hostname = line.split()[3]
        cursor.execute(
            """
        INSERT into autoplot_timing (appid, valid, timing, uri, hostname)
        VALUES (%s, %s, %s, %s, %s)
        """,
            (appid, valid, timing, uri, hostname),
        )
        inserts += 1
    # Don't complain during the early morning hours
    if inserts == 0 and now.hour > 5:
        print(
            ("mine_autoplot: no new entries found for databasing " "since %s")
            % (dbendts)
        )


def main():
    """Go Main Go!"""
    mesosite = get_dbconn("mesosite")
    cursor = mesosite.cursor()
    dbendts = get_dbendts(cursor)
    find_and_save(cursor, dbendts)
    cursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
