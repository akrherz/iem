"""See if MADIS knows any station metadata."""

import datetime
import os
import warnings

from netCDF4 import chartostring
from pandas import read_sql
from pyiem.util import get_sqlalchemy_conn, ncopen, utc

warnings.filterwarnings("ignore", category=DeprecationWarning)


def main():
    """Go Main Go!"""
    with get_sqlalchemy_conn("hads") as conn:
        udf = read_sql(
            """
            SELECT distinct nwsli, 1 as col from unknown
            WHERE length(nwsli) = 5 ORDER by nwsli
        """,
            conn,
            index_col="nwsli",
        )
    print(f"Found {len(udf.index)} unknown entries")
    # Find latest MADIS netcdf
    now = utc()
    i = 0
    while i < 10:
        now -= datetime.timedelta(hours=1)
        testfn = now.strftime("/mesonet/data/madis/mesonet1/%Y%m%d_%H00_10.nc")
        if os.path.isfile(testfn):
            break
        i += 1
    with ncopen(testfn) as nc:
        stations = chartostring(nc.variables["stationId"][:]).tolist()
        names = chartostring(nc.variables["stationName"][:])
        providers = chartostring(nc.variables["dataProvider"][:])
        lats = nc.variables["latitude"][:]
        lons = nc.variables["longitude"][:]
    for sid in udf.index.values:
        if sid not in stations:
            continue
        idx = stations.index(sid)
        print(f"{sid} {names[idx]} {providers[idx]} {lats[idx]} {lons[idx]}")


if __name__ == "__main__":
    main()
