"""
 Look at the sources saved to the AFOS database and then whine about
 sources we do not understand!
"""
import sys
import datetime

import pytz
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, utc, logger

LOG = logger()
pgconn = get_dbconn("afos")
cursor = pgconn.cursor()
cursor2 = pgconn.cursor()

nt = NetworkTable(["WFO", "RFC", "NWS", "NCEP", "CWSU", "WSO"])


def sample(source, ts):
    """ Print out something to look at """
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
        valid = row[1].astimezone(pytz.UTC)
        uri = (
            "https://mesonet.agron.iastate.edu/p.php?pid=%s-%s-%s-%s" ""
        ) % (valid.strftime("%Y%m%d%H%M"), source, row[2], row[0])
        print(" %s" % (uri,))


def look4(ts):
    """ Let us investigate """
    cursor.execute(
        "SELECT source, count(*) from products WHERE entered >= %s "
        "and entered < %s and source is not null "
        "GROUP by source ORDER by count DESC",
        (ts, ts + datetime.timedelta(hours=24)),
    )
    for row in cursor:
        source = row[0]
        lookup = source[1:] if source[0] == "K" else source
        if lookup not in nt.sts and source[0] in ["K", "P"]:
            print("%s %s" % (row[0], row[1]))
            sample(source, ts)


def main(argv):
    """ Go Main Go """
    if len(argv) == 4:
        ts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        ts = utc() - datetime.timedelta(days=1)
        ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)

    LOG.debug("running for %s", ts)
    look4(ts)


if __name__ == "__main__":
    main(sys.argv)
