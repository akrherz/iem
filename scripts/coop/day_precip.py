"""
Daily precip something
"""
import os
import datetime
import subprocess
import tempfile

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    nt = NetworkTable("IA_COOP")
    iem_dbconn = get_dbconn("iem")
    icursor = iem_dbconn.cursor()
    coop_dbconn = get_dbconn("coop")
    ccursor = coop_dbconn.cursor()

    tmpfd = tempfile.NamedTemporaryFile(delete=False, mode="w")
    tmpfd.write("IEMNWSDPR\n")
    tmpfd.write("IOWA ENVIRONMENTAL MESONET\n")
    tmpfd.write("   NWS COOP STATION DAY PRECIPITATION TOTALS\n")
    tmpfd.write("   AS CALCULATED ON THE IEM SERVER\n")

    now = datetime.datetime.now()

    # Now we load climatology
    mrain = {}
    ccursor.execute(
        "select station, avg(precip) as rain from alldata_ia WHERE sday = %s "
        "GROUP by station",
        (now.strftime("%m%d"),),
    )
    for row in ccursor:
        mrain[row[0]] = row[1]

    dt = now.strftime("%d %b %Y").upper()
    tmpfd.write(f"   VALID AT 7AM ON: {dt}\n\n")
    tmpfd.write(
        f"{'ID':6s}{'STATION':24s}{'PREC (IN)':10s}"
        f"{'CLIMO4DATE':11s}{'DIFF':10s}\n"
    )

    queryStr = f"""
        SELECT id,  pday  as prectot from summary_{now.year} s
        JOIN stations t ON (t.iemid = s.iemid)
        WHERE day = '{now:%Y-%m-%d}' and t.network = 'IA_COOP' and pday >= 0
    """

    icursor.execute(queryStr)

    d = {}
    for row in icursor:
        thisStation = row[0]
        thisPrec = row[1]
        if thisStation in nt.sts:
            d[thisStation] = {"prectot": thisPrec}
            d[thisStation]["name"] = nt.sts[thisStation]["name"]
            d[thisStation]["crain"] = mrain[
                nt.sts[thisStation]["climate_site"]
            ]

    keys = list(d.keys())
    keys.sort()

    for k in keys:
        item = d[k]
        diff = item["prectot"] - item["crain"]
        tmpfd.write(
            f"{k:6s}{item['name']:24.24s}{item['prectot']:10.2f}"
            f"{item['crain']:11.2f}{diff:10.2f}\n"
        )

    tmpfd.write(".END\n")
    tmpfd.close()
    subprocess.call(
        [
            "pqinsert",
            "-p",
            "data c 000000000000 text/IEMNWSDPR.txt bogus txt",
            tmpfd.name,
        ]
    )
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
