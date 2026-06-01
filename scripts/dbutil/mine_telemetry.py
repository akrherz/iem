"""Database log entries for telemetry found with syslog

Run from RUN_5MIN.sh
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pyiem.database import get_dbconn
from pyiem.reference import ISO8601
from pyiem.util import logger, utc
from pyiem.webutil import TELEMETRY

LOG = logger()
PREFIX = "Telemetry"


def parse_telemetry_line(line: str):
    """Parse json payload."""
    pos = line.find(PREFIX)
    if pos > -1:
        try:
            payload = json.loads(line[pos + len(PREFIX) :].strip())
            payload["valid"] = datetime.strptime(
                payload["valid"], ISO8601
            ).replace(tzinfo=timezone.utc)
            return TELEMETRY(**payload)
        except (KeyError, TypeError, ValueError) as exp:
            LOG.debug("Skipping malformed telemetry payload: %s", exp)
            return None
    return None


def archive(cursor):
    """Move data out of the way."""
    begints = utc() - timedelta(days=1)
    cursor.execute(
        "DELETE from website_telemetry where valid < %s", (begints,)
    )
    LOG.info("Deleted %s rows prior to %s", cursor.rowcount, begints)


def get_dbendts(cursor):
    """Figure out when we have data until"""
    cursor.execute("SELECT max(valid) from website_telemetry")
    ts = cursor.fetchone()[0]
    if ts is None:
        ts = datetime.now(timezone.utc) - timedelta(hours=1)
    return ts.astimezone(timezone.utc)


def find_and_save(cursor, dbendts: datetime):
    """Do work please"""
    utcnow = datetime.now(timezone.utc)
    inserts = 0
    while dbendts < utcnow:
        fn = Path(f"/var/log/app/telemetry/{dbendts:%Y-%m-%d-%H}.log")
        if not fn.exists():
            LOG.warning("%s does not exist", fn)
        else:
            with open(fn) as fh:
                for line in fh:
                    telemetry = parse_telemetry_line(line)
                    if telemetry is None:
                        continue
                    if telemetry.valid > utcnow or telemetry.valid <= dbendts:
                        continue
                    cursor.execute(
                        """
                        insert into website_telemetry
                        (valid, timing, status_code,
                        client_addr, app, request_uri, vhost)
                        values (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            telemetry.valid,
                            telemetry.timing,
                            telemetry.status_code,
                            telemetry.client_addr,
                            telemetry.app,
                            telemetry.request_uri,
                            telemetry.vhost,
                        ),
                    )
                    inserts += 1
        dbendts = (dbendts + timedelta(hours=1)).replace(
            minute=0, second=0, microsecond=0
        )
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
