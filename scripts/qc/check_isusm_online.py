"""
Check the status of our ISUSM sites being offline or online
run from RUN_40_AFTER.sh
"""
import datetime

from pyiem.network import Table as NetworkTable
from pyiem.tracker import TrackerEngine
from pyiem.util import get_dbconnc, utc


def main():
    """Go Main Go"""
    nt = NetworkTable("ISUSM")
    IEM, icursor = get_dbconnc("iem")
    PORTFOLIO, pcursor = get_dbconnc("portfolio")

    threshold = utc() - datetime.timedelta(hours=12)

    icursor = IEM.cursor()
    icursor.execute(
        "SELECT id, valid from current c JOIN stations t ON "
        "(t.iemid = c.iemid) WHERE t.network = 'ISUSM'"
    )
    obs = {}
    for row in icursor:
        obs[row["id"]] = {"id": row["id"], "valid": row["valid"]}

    tracker = TrackerEngine(icursor, pcursor, 7)
    tracker.process_network(obs, "isusm", nt, threshold)
    tracker.send_emails()
    tac = tracker.action_count
    if tac > 6:
        print(f"check_isusm_online.py had {tac} actions, did not email")
    IEM.commit()
    PORTFOLIO.commit()


if __name__ == "__main__":
    main()
