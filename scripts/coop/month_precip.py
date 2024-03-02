"""
Monthly precip something
"""

import datetime
import os
import subprocess

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def write_data(fp, ccursor, icursor):
    """Write data to fp."""
    nt = NetworkTable("IA_COOP")
    now = datetime.datetime.now()
    fp.write("IEMNWSMPR\n")
    fp.write("IOWA ENVIRONMENTAL MESONET\n")
    fp.write("   NWS COOP STATION MONTH PRECIPITATION TOTALS\n")
    fp.write("   AS CALCULATED ON THE IEM SERVER ...NOTE THE OBS COUNT...\n")

    mrain = {}
    for row in ccursor:
        mrain[row[0]] = row[1]

    fp.write(f"   VALID FOR MONTH OF: {now:%d %B %Y}\n\n")
    fp.write(
        f"{'ID':6s}{'STATION':.24s}{'REPORTS':9s}{'PREC (IN)':10s}"
        f"{'CLIMO2DATE':11s}{'DIFF':10s}\n"
    )
    d = {}
    for row in icursor:
        thisStation = row[0]
        thisPrec = row[2]
        thisCount = row[1]
        if thisStation in nt.sts:
            climate_site = nt.sts[thisStation]["climate_site"]
            if climate_site not in mrain:
                LOG.warning("climate_site has no data: %s", climate_site)
                continue
            d[thisStation] = {"prectot": thisPrec, "cnt": thisCount}
            d[thisStation]["name"] = nt.sts[thisStation]["name"]
            d[thisStation]["crain"] = mrain[
                nt.sts[thisStation]["climate_site"]
            ]

    keys = list(d.keys())
    keys.sort()

    for k in keys:
        item = d[k]
        diff = item["prectot"] - item["crain"]
        fp.write(
            f"{k:6s}{item['name']:.24s}{item['cnt']:9.0f}"
            f"{item['prectot']:10.2f}{item['crain']:11.2f}{diff:10.2f}\n"
        )

    fp.write(".END\n")


def main():
    """Go Main Go"""
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    coop_pgconn = get_dbconn("coop")
    ccursor = coop_pgconn.cursor()
    now = datetime.datetime.now()
    ccursor.execute(
        """
        select station, sum(precip) as rain from climate WHERE
        extract(month from valid) = %s and extract(day from valid) <= %s
        GROUP by station
    """,
        (now.month, now.day),
    )
    icursor.execute(
        f"""
        SELECT id, count(id) as cnt,
        sum(CASE WHEN pday >= 0 THEN pday ELSE 0 END) as prectot
        from summary_{now.year} s JOIN stations t on (t.iemid = s.iemid)
        WHERE date_part('month', day) =
            date_part('month', CURRENT_TIMESTAMP::date)
        and pday >= 0 and t.network = 'IA_COOP' GROUP by id
        """
    )

    with open("IEMNWSMPR.txt", "w", encoding="ascii") as fp:
        write_data(fp, ccursor, icursor)
    subprocess.call(
        [
            "pqinsert",
            "-p",
            "plot c 000000000000 text/IEMNWSMPR.txt bogus txt",
            "IEMNWSMPR.txt",
        ]
    )

    os.unlink("IEMNWSMPR.txt")


if __name__ == "__main__":
    main()
