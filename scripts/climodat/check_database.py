"""Rectify climodat database entries."""
from __future__ import print_function
from io import StringIO
import subprocess
import sys

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def delete_data(pgconn, station, state):
    """Remove whatever data we have for this station."""
    cursor = pgconn.cursor()
    cursor.execute(
        """
    DELETE from alldata_"""
        + state
        + """ WHERE station = %s
    """,
        (station,),
    )
    print("Removed %s database entries" % (cursor.rowcount,))
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go Main"""
    state = argv[1]
    nt = NetworkTable("%sCLIMATE" % (state,))
    pgconn = get_dbconn("coop")
    df = read_sql(
        """
        SELECT station, year, day from alldata_"""
        + state
        + """
        ORDER by station, day
    """,
        pgconn,
        index_col=None,
        parse_dates=["day"],
    )

    for station, gdf in df.groupby("station"):
        if station not in nt.sts:
            print(
                "station: %s is unknown to %sCLIMATE network"
                % (station, state)
            )
            delete_data(pgconn, station, state)
            continue
        # Make sure that our data archive starts on the first of a month
        minday = gdf["day"].min().replace(day=1)
        days = pd.date_range(minday, gdf["day"].max())
        missing = [x for x in days.values if x not in gdf["day"].values]
        print(
            ("station: %s has %s rows between: %s and %s, missing %s/%s days")
            % (
                station,
                len(gdf.index),
                gdf["day"].min(),
                gdf["day"].max(),
                len(missing),
                len(days.values),
            )
        )
        coverage = len(missing) / float(len(days.values))
        if coverage > 0.33:
            cmd = ("python ../dbutil/delete_station.py %sCLIMATE %s") % (
                state,
                station,
            )
            print(cmd)
            subprocess.call(cmd, shell=True)
            delete_data(pgconn, station, state)
            continue
        sio = StringIO()
        for day in missing:
            now = pd.Timestamp(day).to_pydatetime()
            sio.write(
                ("%s,%s,%s,%s,%s\n")
                % (
                    station,
                    now,
                    "%02i%02i" % (now.month, now.day),
                    now.year,
                    now.month,
                )
            )
        sio.seek(0)
        cursor = pgconn.cursor()
        cursor.copy_from(
            sio,
            "alldata_%s" % (state,),
            columns=("station", "day", "sday", "year", "month"),
            sep=",",
        )
        del sio
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
