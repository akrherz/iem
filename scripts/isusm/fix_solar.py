"""Some of our solar radiation data is not good!"""
import datetime
import json
import sys

import requests
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def check_date(date):
    """Look this date over and compare with IEMRE."""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    nt = NetworkTable("ISUSM")
    cursor.execute(
        "SELECT station, slrkj_tot_qc from sm_daily where "
        "valid = %s ORDER by station ASC",
        (date,),
    )
    for row in cursor:
        station = row[0]
        if station not in nt.sts:
            LOG.info("fix_solar station table does not know %s", station)
            continue
        ob = row[1]
        # Go fetch me the IEMRE value!
        uri = (
            f"http://iem.local/iemre/daily/{date:%Y-%m-%d}/"
            f"{nt.sts[station]['lat']:.2f}/"
            f"{nt.sts[station]['lon']:.2f}/json"
        )
        res = requests.get(uri, timeout=60)
        j = json.loads(res.content)
        if j["data"][0]["srad_mj"] is None:
            LOG.info("fix_solar %s %s estimate is missing", station, date)
            continue
        estimate = j["data"][0]["srad_mj"] * 1000.0
        # Never pull data down
        if ob is not None and ob > estimate:
            continue
        # If ob is greater than 5 or the difference is less than 7 <arb>
        if ob is not None and (ob > 5000 or (estimate - ob) < 7000):
            continue
        LOG.info("%s %s Ob:%s Est:%.1f", station, date, ob, estimate)
        cursor2.execute(
            "UPDATE sm_daily SET slrkj_tot_qc = %s, slrkj_tot_f = 'E' "
            "WHERE station = %s and valid = %s",
            (estimate, station, date),
        )

    cursor2.close()
    pgconn.commit()


def fix_nulls():
    """Correct any nulls."""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    nt = NetworkTable("ISUSM")
    cursor.execute(
        """
        SELECT station, valid from sm_daily where (slrkj_tot_qc is null or
        slrkj_tot_qc < 0.1 or slrkj_tot_qc > 35000)
        and valid > '2019-04-14' ORDER by valid ASC
    """
    )
    for row in cursor:
        station = row[0]
        v1 = datetime.datetime(row[1].year, row[1].month, row[1].day)
        v2 = v1.replace(hour=23, minute=59)
        cursor2.execute(
            """
            SELECT sum(slrkj_tot_qc), count(*) from sm_hourly WHERE
            station = %s and valid >= %s and valid < %s
        """,
            (station, v1, v2),
        )
        row2 = cursor2.fetchone()
        if row2[0] is None or row2[0] < 0.01:
            LOG.warning(
                "%s %s summed %s hourly for solar, using IEMRE",
                station,
                v1.strftime("%d %b %Y"),
                row2[0],
            )
            if station not in nt.sts:
                LOG.warning("unknown station %s metadata, skipping", station)
                continue
            # Go fetch me the IEMRE value!
            uri = (
                f"http://iem.local/iemre/daily/{v1:%Y-%m-%d}/"
                f"{nt.sts[station]['lat']:.2f}/"
                f"{nt.sts[station]['lon']:.2f}/json"
            )
            res = requests.get(uri, timeout=60)
            if res.status_code != 200:
                LOG.warning("Fix solar got %s from %s", res.status_code, uri)
                continue
            j = json.loads(res.content)
            if not j["data"]:
                LOG.warning(
                    "fix solar: No data for %s %s",
                    station,
                    v1.strftime("%d %b %Y"),
                )
                continue
            row2 = [j["data"][0]["srad_mj"], -1]
        if row2[0] is None or row2[0] < 0.01:
            LOG.info("Triple! Failure %s %s", station, v1.strftime("%d %b %Y"))
            continue
        LOG.warning(
            "%s %s -> %.2f (%s obs)",
            station,
            v1.strftime("%d %b %Y"),
            row2[0],
            row2[1],
        )
        if row2[0] > 35000:
            LOG.warning("New value %s too large, skipping", row2[0])
            continue
        cursor2.execute(
            "UPDATE sm_daily SET slrkj_tot_qc = %s "
            "WHERE station = %s and valid = %s",
            (row2[0], station, row[1]),
        )

    cursor2.close()
    pgconn.commit()


def main(argv):
    """Go Main Go."""
    # if we are given an argument, run for that date
    if len(argv) == 4:
        check_date(datetime.date(int(argv[1]), int(argv[2]), int(argv[3])))
    else:
        # Correct any nulls in the database
        fix_nulls()


if __name__ == "__main__":
    main(sys.argv)
