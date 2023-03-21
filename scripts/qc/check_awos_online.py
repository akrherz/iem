"""
Check the status of our AWOS sites being offline or online
run from RUN_10_AFTER.sh
"""
import datetime

from pyiem.tracker import TrackerEngine
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, utc, logger

LOG = logger()


def main():
    """Go Main Go"""
    nt = NetworkTable("IA_ASOS")
    IEM = get_dbconn("iem")
    PORTFOLIO = get_dbconn("portfolio")

    threshold = utc() - datetime.timedelta(hours=1)

    icursor = IEM.cursor()
    icursor.execute(
        "SELECT id, valid from current c JOIN stations t ON "
        "(t.iemid = c.iemid) WHERE t.network = 'IA_ASOS' and t.online"
    )
    obs = {}
    for row in icursor:
        if nt.sts[row[0]]["attributes"].get("IS_AWOS") == "1":
            obs[row[0]] = {"id": row[0], "valid": row[1]}

    tracker = TrackerEngine(IEM.cursor(), PORTFOLIO.cursor(), 10)
    tracker.process_network(obs, "iaawos", nt, threshold)
    tracker.send_emails()
    tac = tracker.action_count
    if tac > 6:
        LOG.warning("Had %s actions, did not email", tac)
    IEM.commit()
    PORTFOLIO.commit()


if __name__ == "__main__":
    main()
