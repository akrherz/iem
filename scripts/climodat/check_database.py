"""
 Check over the database and make sure we have what we need there to
 make the climodat reports happy...
"""
from __future__ import print_function
import sys

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main(argv):
    """Go Main"""
    state = argv[1]
    nt = NetworkTable("%sCLIMATE" % (state,))
    pgconn = get_dbconn('coop')
    cursor = pgconn.cursor()
    df = read_sql("""
        SELECT station, year, day from alldata_""" + state + """
        ORDER by station, day
    """, pgconn, index_col=None, parse_dates=['day'])

    for station, gdf in df.groupby('station'):
        if station not in nt.sts:
            print("station: %s is unknown to %sCLIMATE network" % (station,
                                                                   state))
            continue
        days = pd.date_range(gdf['day'].min(), gdf['day'].max())
        missing = [x for x in days.values if x not in gdf['day'].values]
        print(("station: %s has %s rows between: %s and %s, missing %s/%s days"
               ) % (station, len(gdf.index), gdf['day'].min(),
                    gdf['day'].max(), len(missing), len(days.values)))
        for day in missing:
            now = pd.Timestamp(day).to_pydatetime()
            cursor.execute("""
                INSERT into alldata_""" + state + """ (station, day, sday,
                year, month) VALUES (%s, %s, %s, %s, %s)
            """, (station, now,
                  "%02i%02i" % (now.month, now.day), now.year, now.month))

    cursor.close()
    pgconn.commit()


if __name__ == '__main__':
    main(sys.argv)
