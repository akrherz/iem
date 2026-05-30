"""Database found apache log entries of autoplot generation timing

Run from RUN_10_AFTER.sh
"""

import json
from datetime import datetime, timedelta

from iemweb.autoplot.autoplot import AUTOPLOT_TIMING
from pyiem.database import get_dbconn
from pyiem.util import logger, utc

LOG = logger()
LOGFN = "/var/log/app/autoplot_log"


def parse_timing_line(line: str):
    """Parse json payload."""
    pos = line.find(AUTOPLOT_TIMING)
    if pos > -1:
        try:
            payload = json.loads(line[pos + len(AUTOPLOT_TIMING) :].strip())
            return (
                payload["appid"],
                payload["timing"],
                payload["uri"],
            )
        except (KeyError, TypeError, ValueError):
            # Producer bounds payload size, but syslog truncation can still
            # leave a partial JSON document in the log file.
            LOG.debug("Skipping malformed autoplot timing payload")
            return None
    return None


def archive(cursor):
    """Move data out of the way."""
    begints = utc() - timedelta(days=10)
    cursor.execute(
        "insert into autoplot_timing_archive select * from autoplot_timing "
        "WHERE valid < %s",
        (begints,),
    )
    cursor.execute("DELETE from autoplot_timing where valid < %s", (begints,))
    LOG.info("Archived %s rows prior to %s", cursor.rowcount, begints)


def get_dbendts(cursor):
    """Figure out when we have data until"""
    cursor.execute("SELECT max(valid) from autoplot_timing")
    ts = cursor.fetchone()[0]
    if ts is None:
        ts = datetime.now() - timedelta(days=1)
    else:
        ts = ts.replace(tzinfo=None)
    return ts


def find_and_save(cursor, dbendts):
    """Do work please"""
    now = datetime.now()
    thisyear = now.year
    inserts = 0
    with open(LOGFN, "rb") as fh:
        for line_in in fh:
            line = line_in.decode("utf-8", "ignore")
            parsed = parse_timing_line(line)
            if parsed is None:
                continue
            (appid, timing, uri) = parsed
            try:
                valid = datetime.strptime(
                    f"{thisyear} {line[:15]}", "%Y %b %d %H:%M:%S"
                )
            except ValueError as exp:
                LOG.info(line)
                LOG.error(exp)
                continue
            if valid > now or valid <= dbendts:
                continue
            hostname = line.split()[3]
            cursor.execute(
                "INSERT into autoplot_timing "
                "(appid, valid, timing, uri, hostname) "
                "VALUES (%s, %s, %s, %s, %s)",
                (appid, valid, timing, uri, hostname),
            )
            inserts += 1
    # Don't complain during the early morning hours
    if inserts == 0 and now.hour > 5:
        LOG.warning(
            "mine_autoplot: no new entries found for databasing since %s",
            dbendts,
        )
    else:
        LOG.info("Inserted %s records", inserts)


def main():
    """Go Main Go!"""
    mesosite = get_dbconn("mesosite")
    cursor = mesosite.cursor()
    dbendts = get_dbendts(cursor)
    find_and_save(cursor, dbendts)
    archive(cursor)
    cursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
