"""
Check to see if there are webcams offline, generate emails and such
"""
import os
import stat
import datetime

import pytz
from pyiem.network import Table as NetworkTable
from pyiem.tracker import TrackerEngine
from pyiem.util import get_dbconn


def workflow(netname, pname):
    """Do something please"""
    pgconn_iem = get_dbconn("iem")
    pgconn_mesosite = get_dbconn("mesosite")
    pgconn_portfolio = get_dbconn("portfolio")

    # Now lets check files
    mydir = "/home/ldm/data/camera/stills"

    threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    threshold = threshold.replace(tzinfo=pytz.UTC)
    mcursor = pgconn_mesosite.cursor()
    mcursor.execute(
        """
        SELECT id, network, name from webcams where
        network = %s
        and online ORDER by id ASC
    """,
        (netname,),
    )
    nt = NetworkTable(None)
    obs = {}
    missing = 0
    for row in mcursor:
        nt.sts[row[0]] = dict(
            id=row[0], network=row[1], name=row[2], tzname="America/Chicago"
        )
        fn = "%s/%s.jpg" % (mydir, row[0])
        if not os.path.isfile(fn):
            missing += 1
            if missing > 1:
                print("Missing webcam file: %s" % (fn,))
            continue
        ticks = os.stat(fn)[stat.ST_MTIME]
        valid = datetime.datetime(1970, 1, 1) + datetime.timedelta(
            seconds=ticks
        )
        valid = valid.replace(tzinfo=pytz.UTC)
        obs[row[0]] = dict(valid=valid)
    # Abort out if no obs are found
    if not obs:
        return

    tracker = TrackerEngine(pgconn_iem.cursor(), pgconn_portfolio.cursor(), 10)
    tracker.process_network(obs, pname, nt, threshold)
    tracker.send_emails()
    pgconn_iem.commit()
    pgconn_portfolio.commit()


def main():
    """Do something"""
    for network in ["KCCI", "KCRG", "KELO", "KCWI"]:
        workflow(network, "%ssnet" % (network.lower(),))


if __name__ == "__main__":
    main()
