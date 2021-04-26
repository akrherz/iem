"""
Monthly precip something
"""
import datetime
import subprocess
import os

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main Go"""
    nt = NetworkTable("IA_COOP")
    iem_pgconn = get_dbconn("iem", user="nobody")
    icursor = iem_pgconn.cursor()
    coop_pgconn = get_dbconn("coop", user="nobody")
    ccursor = coop_pgconn.cursor()

    o = open("IEMNWSMPR.txt", "w")
    o.write("IEMNWSMPR\n")
    o.write("IOWA ENVIRONMENTAL MESONET\n")
    o.write("   NWS COOP STATION MONTH PRECIPITATION TOTALS\n")
    o.write("   AS CALCULATED ON THE IEM SERVER ...NOTE THE OBS COUNT...\n")

    now = datetime.datetime.now()

    # Now we load climatology
    mrain = {}
    ccursor.execute(
        """
        select station, sum(precip) as rain from climate WHERE
        extract(month from valid) = %s and extract(day from valid) <= %s
        GROUP by station
    """
        % (now.month, now.day)
    )
    for row in ccursor:
        mrain[row[0]] = row[1]

    o.write(
        ("   VALID FOR MONTH OF: %s\n\n") % (now.strftime("%d %B %Y").upper(),)
    )
    o.write(
        "%-6s%-24.24s%9s%10s%11s%10s\n"
        % ("ID", "STATION", "REPORTS", "PREC (IN)", "CLIMO2DATE", "DIFF")
    )

    icursor.execute(
        """
        SELECT id, count(id) as cnt,
        sum(CASE WHEN pday >= 0 THEN pday ELSE 0 END) as prectot
        from summary_%s s JOIN stations t on (t.iemid = s.iemid)
        WHERE date_part('month', day) =
            date_part('month', CURRENT_TIMESTAMP::date)
        and pday >= 0 and t.network = 'IA_COOP' GROUP by id
        """
        % (now.year,)
    )

    d = {}
    for row in icursor:
        thisStation = row[0]
        thisPrec = row[2]
        thisCount = row[1]
        if thisStation in nt.sts:
            climate_site = nt.sts[thisStation]["climate_site"]
            if climate_site not in mrain:
                LOG.debug("climate_site has no data: %s", climate_site)
                continue
            d[thisStation] = {"prectot": thisPrec, "cnt": thisCount}
            d[thisStation]["name"] = nt.sts[thisStation]["name"]
            d[thisStation]["crain"] = mrain[
                nt.sts[thisStation]["climate_site"]
            ]

    keys = list(d.keys())
    keys.sort()

    for k in keys:
        o.write(
            ("%-6s%-24.24s%9.0f%10.2f%11.2f%10.2f\n")
            % (
                k,
                d[k]["name"],
                d[k]["cnt"],
                d[k]["prectot"],
                d[k]["crain"],
                d[k]["prectot"] - d[k]["crain"],
            )
        )

    o.write(".END\n")
    o.close()

    subprocess.call(
        (
            "pqinsert -p 'plot c 000000000000 "
            "text/IEMNWSMPR.txt bogus txt' IEMNWSMPR.txt"
        ),
        shell=True,
    )

    os.unlink("IEMNWSMPR.txt")


if __name__ == "__main__":
    main()
