"""Use IEMRE estimated high and low temps"""

import json

import httpx
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value, get_dbconn, logger

LOG = logger()


def main():
    """Go main go"""
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
        uri = (
            "http://mesonet.agron.iastate.edu/iemre/daily/"
            f"{date:%Y-%m-%d}/{nt.sts[station]['lat']:.2f}/"
            f"{nt.sts[station]['lon']:.2f}/json"
        )
        res = httpx.get(uri, timeout=60)
        j = json.loads(res.content)
        if not j["data"]:
            LOG.info(" %s %s IEMRE Failure", station, date)
            continue
        highf = j["data"][0]["daily_high_f"]
        lowf = j["data"][0]["daily_low_f"]
        LOG.info(" %s %s high: %.1f low: %.1f", station, date, highf, lowf)
        high = convert_value(highf, "degF", "degC")
        low = convert_value(lowf, "degF", "degC")
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
