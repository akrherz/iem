"""See if we have metadata from HOMR

https://www.ncdc.noaa.gov/homr/reports
"""
from __future__ import print_function

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main():
    """Go Main Go!"""
    pgconn = get_dbconn('hads')
    udf = read_sql("""
        SELECT distinct nwsli, 1 as col from unknown
        WHERE length(nwsli) = 5 ORDER by nwsli
    """, pgconn, index_col='nwsli')
    print("Found %s unknown entries" % (len(udf.index), ))
    for line in open("/home/akrherz/Downloads/mshr_enhanced_201907.txt"):
        if len(line) < 10:
            continue
        nwsli = line[155:174].strip()
        enddate = line[41:49]
        state = line[778:788].strip()
        country = line[843:845]
        try:
            lat = float(line[1299:1319])
            lon = float(line[1320:1340])
        except ValueError:
            lat = line[1299:1319]
            lon = line[1320:1340]
        name = line[260:360].strip()
        platform = line[1473:1572].strip()
        if nwsli in udf.index:
            print("%s %s %s %s %s %s %s %s" % (
                nwsli, enddate, state, country, name, platform, lat, lon))


if __name__ == '__main__':
    main()
