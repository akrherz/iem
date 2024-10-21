"""
Check to see if there are webcams offline, generate emails and such
"""

import os
import stat
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable
from pyiem.tracker import TrackerEngine
from pyiem.util import utc


def workflow(netname, pname):
    """Do something please"""
    pgconn_iem, icursor = get_dbconnc("iem")
    pgconn_mesosite, mcursor = get_dbconnc("mesosite")
    pgconn_portfolio, pcursor = get_dbconnc("portfolio")

    # Now lets check files
    mydir = "/mesonet/ldmdata/camera/stills"

    threshold = utc() - timedelta(hours=2)
    mcursor.execute(
        "SELECT id, network, name from webcams where network = %s and online "
        "ORDER by id ASC",
        (netname,),
    )
    nt = NetworkTable(None)
    obs = {}
    missing = 0
    for row in mcursor:
        nt.sts[row["id"]] = dict(
            id=row["id"],
            network=row["network"],
            name=row["name"],
            tzname="America/Chicago",
        )
        fn = f"{mydir}/{row['id']}.jpg"
        if not os.path.isfile(fn):
            missing += 1
            if missing > 1:
                print(f"Missing webcam file: {fn}")
            continue
        ticks = os.stat(fn)[stat.ST_MTIME]
        valid = datetime(1970, 1, 1) + timedelta(seconds=ticks)
        valid = valid.replace(tzinfo=ZoneInfo("UTC"))
        obs[row["id"]] = {"valid": valid}
    # Abort out if no obs are found
    if not obs:
        return

    tracker = TrackerEngine(icursor, pcursor, 10)
    tracker.process_network(obs, pname, nt, threshold)
    tracker.send_emails()
    pgconn_iem.commit()
    pgconn_portfolio.commit()
    pgconn_mesosite.close()


def main():
    """Do something"""
    for network in ["KCCI", "KCRG", "KELO", "KCWI"]:
        workflow(network, f"{network.lower()}snet")


if __name__ == "__main__":
    main()
