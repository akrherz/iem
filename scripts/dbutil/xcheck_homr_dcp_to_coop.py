"""If HOMR says a site is a COOP, we will believe it, sometimes.

https://www.ncdc.noaa.gov/homr/reports
"""
from __future__ import print_function
import sys

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go!"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    df = read_sql(
        """
        SELECT id, count(*), max(network) as network from stations
        WHERE network ~* 'COOP' or network ~* 'DCP'
        GROUP by id ORDER by id ASC
    """,
        pgconn,
        index_col="id",
    )
    print("Found %s entries" % (len(df.index),))
    done = []
    for line in open("/home/akrherz/Downloads/mshr_enhanced_201907.txt"):
        if len(line) < 10:
            continue
        nwsli = line[155:174].strip()
        enddate = line[41:49]
        state = line[778:788].strip()
        country = line[843:845]
        name = line[260:360].strip()
        platform = line[1473:1572].strip()
        if (
            nwsli in df.index
            and df.at[nwsli, "count"] == 1
            and str(df.at[nwsli, "network"]).find("_DCP") > 0
        ):
            if nwsli in done:
                continue
            done.append(nwsli)
            print(
                "%s %s %s %s %s %s"
                % (nwsli, enddate, state, country, name, platform)
            )
            cursor.execute(
                """
                UPDATE stations SET network = %s WHERE id = %s and network = %s
            """,
                (
                    str(df.at[nwsli, "network"]).replace("_DCP", "_COOP"),
                    nwsli,
                    str(df.at[nwsli, "network"]),
                ),
            )
            if cursor.rowcount != 1:
                print("ABORT")
                sys.exit()
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
