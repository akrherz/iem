"""Yearly precip something"""
from __future__ import print_function
import datetime
import subprocess
import os

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    nt = NetworkTable("IA_COOP")
    iem_pgconn = get_dbconn("iem", user="nobody")
    icursor = iem_pgconn.cursor()
    coop_pgconn = get_dbconn("coop", user="nobody")
    ccursor = coop_pgconn.cursor()

    fp = open("IEMNWSYPR.txt", "w")
    fp.write("IEMNWSYPR\n")
    fp.write("IOWA ENVIRONMENTAL MESONET\n")
    fp.write("   NWS COOP STATION YEAR PRECIPITATION TOTALS\n")
    fp.write("   AS CALCULATED ON THE IEM SERVER\n")

    now = datetime.datetime.now()
    jdays = now.strftime("%j")

    mrain = {}
    ccursor.execute(
        """
        select station, sum(precip) as rain from climate WHERE
        valid <= '%s'
        GROUP by station
    """
        % (now.strftime("2000-%m-%d"),)
    )
    for row in ccursor:
        mrain[row[0]] = row[1]

    fp.write("   TOTAL REPORTS POSSIBLE: %s\n" % (jdays))

    fp.write("   VALID FOR YEAR THRU: %s\n\n" % (now.strftime("%d %B %Y"),))
    fp.write(
        ("%-6s%-24.24s%9s%10s%11s%10s\n")
        % ("ID", "STATION", "REPORTS", "PREC (IN)", "CLIMO2DATE", "DIFF")
    )

    icursor.execute(
        """
        SELECT id, count(id) as cnt,
        sum(CASE WHEN pday > 0 THEN pday ELSE 0 END) as prectot
        from summary_%s s JOIN stations t ON (s.iemid = t.iemid)
        WHERE t.network = 'IA_COOP' and pday >= 0
        GROUP by id"""
        % (now.year,)
    )

    data = {}
    for row in icursor:
        station = row[0]
        prec = row[2]
        count = row[1]
        if station in nt.sts:
            data[station] = {"prectot": prec, "cnt": count}
            data[station]["name"] = nt.sts[station]["name"]
            data[station]["crain"] = mrain[nt.sts[station]["climate_site"]]

    keys = list(data.keys())
    keys.sort()

    for k in keys:
        fp.write(
            ("%-6s%-24.24s%9.0f%10.2f%11.2f%10.2f\n")
            % (
                k,
                data[k]["name"],
                data[k]["cnt"],
                data[k]["prectot"],
                data[k]["crain"],
                data[k]["prectot"] - data[k]["crain"],
            )
        )

    fp.write(".END\n")
    fp.close()

    subprocess.call(
        (
            "/home/ldm/bin/pqinsert -p 'plot c 000000000000 "
            "text/IEMNWSYPR.txt bogus txt' IEMNWSYPR.txt"
        ),
        shell=True,
    )

    os.unlink("IEMNWSYPR.txt")


if __name__ == "__main__":
    main()
