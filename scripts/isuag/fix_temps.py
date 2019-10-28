"""Use IEMRE estimated high and low temps"""
from __future__ import print_function
import json

import requests
from pyiem.datatypes import temperature
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main():
    """ Go main go """
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    nt = NetworkTable("ISUSM")
    cursor.execute(
        """
     SELECT station, valid from sm_daily where (tair_c_avg_qc is null or
     tair_c_min_qc is null or tair_c_max_qc is null) ORDER by valid ASC
    """
    )
    for row in cursor:
        station = row[0]
        date = row[1]
        # Go fetch me the IEMRE value!
        uri = ("http://iem.local/iemre/daily/%s/%.2f/%.2f/json") % (
            date.strftime("%Y-%m-%d"),
            nt.sts[station]["lat"],
            nt.sts[station]["lon"],
        )
        res = requests.get(uri)
        j = json.loads(res.content)
        if not j["data"]:
            print(" %s %s IEMRE Failure" % (station, date))
            continue
        highf = j["data"][0]["daily_high_f"]
        lowf = j["data"][0]["daily_low_f"]
        print(" %s %s high: %.1f low: %.1f" % (station, date, highf, lowf))
        high = temperature(highf, "F").value("C")
        low = temperature(lowf, "F").value("C")
        avg = (high + low) / 2.0
        cursor2.execute(
            """
            UPDATE sm_daily SET
            tair_c_avg_qc = %s,
            tair_c_min_qc = %s,
            tair_c_max_qc = %s,
            tair_c_avg_f = 'e',
            tair_c_min_f = 'e',
            tair_c_max_f = 'e'
            WHERE station = %s and valid = %s
        """,
            (avg, low, high, station, date),
        )

    cursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
