"""Yearly precip something"""
import datetime
import subprocess
import os

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    nt = NetworkTable("IA_COOP")
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    coop_pgconn = get_dbconn("coop")
    ccursor = coop_pgconn.cursor()

    with open("IEMNWSYPR.txt", "w", encoding="ascii") as fp:
        fp.write("IEMNWSYPR\n")
        fp.write("IOWA ENVIRONMENTAL MESONET\n")
        fp.write("   NWS COOP STATION YEAR PRECIPITATION TOTALS\n")
        fp.write("   AS CALCULATED ON THE IEM SERVER\n")

        now = datetime.datetime.now()
        jdays = now.strftime("%j")

        mrain = {}
        ccursor.execute(
            f"""
            select station, sum(precip) as rain from climate WHERE
            valid <= '2000-{now:%m-%d}'
            GROUP by station
        """
        )
        for row in ccursor:
            mrain[row[0]] = row[1]

        fp.write(f"   TOTAL REPORTS POSSIBLE: {jdays}\n")

        fp.write(f"   VALID FOR YEAR THRU: {now:%d %B %Y}\n\n")
        fp.write(
            f"{'ID':<6s}{'STATION':<24.24s}{'REPORTS':9s}"
            f"{'PREC (IN)':10s}{'CLIMO2DATE':11s}{'DIFF':10s}\n"
        )

        icursor.execute(
            f"""
            SELECT id, count(id) as cnt,
            sum(CASE WHEN pday > 0 THEN pday ELSE 0 END) as prectot
            from summary_{now.year} s JOIN stations t ON (s.iemid = t.iemid)
            WHERE t.network = 'IA_COOP' and pday >= 0
            GROUP by id"""
        )

        data = {}
        for row in icursor:
            station = row[0]
            prec = row[2]
            count = row[1]
            if station in nt.sts:
                clstation = nt.sts[station]["climate_site"]
                if clstation not in mrain:
                    continue
                data[station] = {"prectot": prec, "cnt": count}
                data[station]["name"] = nt.sts[station]["name"]
                data[station]["crain"] = mrain[clstation]

        keys = list(data.keys())
        keys.sort()

        for k in keys:
            item = data[k]
            diff = item["prectot"] - item["crain"]
            fp.write(
                f"{k:<6s}{item['name']:<24.24s}{item['cnt']:9.0f}"
                f"{item['prectot']:10.2f}{item['crain']:11.2f}"
                f"{diff:10.2f}\n"
            )

        fp.write(".END\n")
    fp.close()

    subprocess.call(
        [
            "pqinsert",
            "-p",
            "plot c 000000000000 text/IEMNWSYPR.txt bogus txt",
            "IEMNWSYPR.txt",
        ]
    )

    os.unlink("IEMNWSYPR.txt")


if __name__ == "__main__":
    main()
