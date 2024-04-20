"""Check AFOS database for problems we don't want.

- [ ] Unknown sources
- [ ] Duplicated VTEC product_ids

called from RUN_MIDNIGHT.sh
"""

import datetime
import sys
from zoneinfo import ZoneInfo

from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger, utc

LOG = logger()
pgconn = get_dbconn("afos")
cursor = pgconn.cursor()
cursor2 = pgconn.cursor()

KNOWN = ["PANC", "PHBK"]
nt = NetworkTable(["WFO", "RFC", "NWS", "NCEP", "CWSU", "WSO"])
BASE = "https://mesonet.agron.iastate.edu/p.php?pid"


def check_vtec_dups(ts):
    """Ensure the database doesn't have duplicated product_id."""
    cursor.execute(
        """
        with data as (
            select entered, source, pil, bbb, count(*) from products
            where entered > %s and entered < %s and
            substr(pil, 1, 3) in ('SVR', 'FFW', 'TOR', 'SVS', 'FLW', 'FFS')
            group by entered, source, pil, bbb)
        select * from data where count > 1
        """,
        (ts - datetime.timedelta(hours=2), ts + datetime.timedelta(hours=26)),
    )
    if cursor.rowcount > 0:
        LOG.warning("Found %s VTEC relevant product_id dups", cursor.rowcount)
    for row in cursor:
        print(f"DUP: {row[0]} {row[1]} {row[2]} {row[3]} {row[4]}")


def sample(source, ts):
    """Print out something to look at"""
    cursor2.execute(
        "SELECT pil, entered, wmo from products where entered >= %s "
        "and entered < %s and source = %s",
        (ts, ts + datetime.timedelta(hours=24), source),
    )
    pils = []
    for row in cursor2:
        if row[0] in pils:
            continue
        pils.append(row[0])
        valid = row[1].astimezone(ZoneInfo("UTC"))
        print(f" {BASE}={valid:%Y%m%d%H%M}-{source}-{row[2]}-{row[0]}")


def look4(ts):
    """Let us investigate"""
    cursor.execute(
        "SELECT source, count(*) from products WHERE entered >= %s "
        "and entered < %s and substr(source, 1, 1) in ('K', 'P') "
        "GROUP by source ORDER by count DESC",
        (ts, ts + datetime.timedelta(hours=24)),
    )
    for row in cursor:
        source = row[0]
        lookup = source[1:] if source[0] == "K" else source
        if lookup in nt.sts:
            continue
        if lookup in KNOWN:
            LOG.info("Skipping known %s", lookup)
            continue
        print(f"{row[0]} {row[1]}")
        sample(source, ts)


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        ts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        ts = utc() - datetime.timedelta(days=1)
        ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)

    LOG.info("running for %s", ts)
    look4(ts)


if __name__ == "__main__":
    main(sys.argv)
