"""Quality control our 4 inch soil temperature data.

Called from XXX
"""

import datetime
import json
import sys

import requests
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value, logger

LOG = logger()


def setval(cursor2, station, ob, date, newval):
    """We have something to set."""
    LOG.warning("%s soil4t %s -> %s [E]", station, ob, newval)
    cursor2.execute(
        """
        UPDATE sm_daily SET t4_c_avg_qc = %s, t4_c_avg_f = 'E' WHERE
        station = %s and valid = %s
        """,
        (newval, station, date),
    )


def check_date(date):
    """Look this date over and compare with IEMRE."""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    nt = NetworkTable("ISUSM")
    cursor.execute(
        "SELECT station, t4_c_avg_qc from sm_daily where "
        "valid = %s ORDER by station ASC",
        (date,),
    )
    for row in cursor:
        station = row[0]
        ob = row[1]

        # Go fetch me the IEMRE value!
        uri = (
            f"http://iem.local/iemre/daily/{date:%Y-%m-%d}/"
            f"{nt.sts[station]['lat']:.2f}/"
            f"{nt.sts[station]['lon']:.2f}/json"
        )
        res = requests.get(uri, timeout=60)
        j = json.loads(res.content)
        iemre = j["data"][0]
        iemre_low = convert_value(iemre["soil4t_low_f"], "degF", "degC")
        iemre_high = convert_value(iemre["soil4t_high_f"], "degF", "degC")
        if iemre_high is None or iemre_low is None:
            LOG.warning("%s %s IEMRE is missing", station, date)
            continue
        iemre_avg = (iemre_high + iemre_low) / 2.0
        # If Ob is None, we have no choice
        if ob is None:
            if nt.sts[station]["attributes"].get("NO_4INCH") == "1":
                LOG.info("Skipping %s as NO_4INCH", station)
                continue
            setval(cursor2, station, ob, date, iemre_avg)
            continue
        # Passes if value within 2 C of IEMRE
        if abs(iemre_avg - ob) <= 2:
            LOG.info("%s passes2c ob:%.2f iemre:%.2f", station, ob, iemre_avg)
            continue
        # Passes if value within 25 to 75th percentile
        lowerbound = iemre_low + (iemre_high - iemre_low) * 0.25
        upperbound = iemre_low + (iemre_high - iemre_low) * 0.75
        if lowerbound <= ob <= upperbound:
            LOG.info("%s passesbnd ob:%.2f iemre:%.2f", station, ob, iemre_avg)
            continue
        # We fail
        setval(cursor2, station, ob, date, iemre_avg)

    cursor2.close()
    pgconn.commit()


def main(argv):
    """Go Main Go."""
    check_date(datetime.date(int(argv[1]), int(argv[2]), int(argv[3])))


if __name__ == "__main__":
    main(sys.argv)
