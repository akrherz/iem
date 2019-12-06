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
    iem_dbconn = get_dbconn("iem", user="nobody")
    icursor = iem_dbconn.cursor()
    coop_dbconn = get_dbconn("coop", user="nobody")
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
        """
        select station, precip as rain from climate WHERE
        valid = '%s'
    """
        % (now.strftime("2000-%m-%d"),)
    )
    for row in ccursor:
        mrain[row[0]] = row[1]

    tmpfd.write(
        "   VALID AT 7AM ON: %s\n\n" % (now.strftime("%d %b %Y").upper(),)
    )
    tmpfd.write(
        "%-6s%-24s%10s%11s%10s\n"
        % ("ID", "STATION", "PREC (IN)", "CLIMO4DATE", "DIFF")
    )

    queryStr = """
        SELECT id,  pday  as prectot from summary_%s s
        JOIN stations t ON (t.iemid = s.iemid)
        WHERE day = '%s' and t.network = 'IA_COOP' and pday >= 0
    """ % (
        now.year,
        now.strftime("%Y-%m-%d"),
    )

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
        tmpfd.write(
            "%-6s%-24.24s%10.2f%11.2f%10.2f\n"
            % (
                k,
                d[k]["name"],
                d[k]["prectot"],
                d[k]["crain"],
                d[k]["prectot"] - d[k]["crain"],
            )
        )

    tmpfd.write(".END\n")
    tmpfd.close()
    subprocess.call(
        ("pqinsert -p 'data c 000000000000 text/IEMNWSDPR.txt bogus txt' %s")
        % (tmpfd.name,),
        shell=True,
    )
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
