"""See if MADIS knows any station metadata."""
import os
import datetime
import warnings

from pandas.io.sql import read_sql
from netCDF4 import chartostring
from pyiem.util import get_dbconn, ncopen, utc

warnings.filterwarnings("ignore", category=DeprecationWarning)


def main():
    """Go Main Go!"""
    pgconn = get_dbconn("hads")
    udf = read_sql(
        """
        SELECT distinct nwsli, 1 as col from unknown
        WHERE length(nwsli) = 5 ORDER by nwsli
    """,
        pgconn,
        index_col="nwsli",
    )
    print("Found %s unknown entries" % (len(udf.index),))
    # Find latest MADIS netcdf
    now = utc()
    i = 0
    while i < 10:
        now -= datetime.timedelta(hours=1)
        testfn = now.strftime("/mesonet/data/madis/mesonet1/%Y%m%d_%H00.nc")
        if os.path.isfile(testfn):
            break
        i += 1
    with ncopen(testfn) as nc:
        stations = chartostring(nc.variables["stationId"][:]).tolist()
        names = chartostring(nc.variables["stationName"][:])
        providers = chartostring(nc.variables["dataProvider"][:])
        latitudes = nc.variables["latitude"][:]
        longitudes = nc.variables["longitude"][:]
    for sid in udf.index.values:
        if sid not in stations:
            continue
        idx = stations.index(sid)
        print(
            "%s %s %s %s %s"
            % (
                sid,
                names[idx],
                providers[idx],
                latitudes[idx],
                longitudes[idx],
            )
        )


if __name__ == "__main__":
    main()
