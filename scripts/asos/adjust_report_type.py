"""Find some misssed report_type=3

Sometimes strange things happen with specials around the time of the routine
report type.  This script attempts to find those and fix em.

Run from `RUN_MIDNIGHT.sh` for previous UTC date.

see akrherz/iem#104
"""
import datetime
import sys

import pandas as pd
from pyiem.util import utc, logger, get_sqlalchemy_conn, get_dbconn

LOG = logger()


def arbpick(asosdb, year, station, gdf):
    """Just pick a date."""
    cursor = asosdb.cursor()
    for _, row in gdf.iterrows():
        cursor.execute(
            f"UPDATE t{year} SET report_type = 3 where station = %s and "
            "valid = %s",
            (station, row["max_valid"]),
        )
    cursor.close()
    asosdb.commit()


def main(argv):
    """Go."""
    sts = utc(*[int(v) for v in argv[1:4]])
    ets = sts + datetime.timedelta(hours=24)
    asosdb = get_dbconn("asos")
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            "SELECT station, date_trunc('hour', valid) as ts, "
            "sum(case when report_type = 3 then 1 else 0 end) as rcount, "
            "sum(case when report_type = 4 then 1 else 0 end) as scount, "
            "min(valid) as min_valid, max(valid) as max_valid "
            "from alldata where valid >= %s and valid < %s and "
            "report_type in (3, 4) "
            "GROUP by station, ts ORDER by station, ts",
            conn,
            params=(sts, ets),
        )
    for station, gdf in df.groupby("station"):
        # Nothing to do
        if gdf["rcount"].min() == 1:
            continue
        # Happy Station Count
        if gdf["rcount"].max() == 1 and gdf["rcount"].sum() == 24:
            continue
        # Life choices
        if len(station) == 4 and gdf["rcount"].sum() == 0:
            arbpick(asosdb, sts.year, station, gdf)
            continue
        # Look for situation of having specials, but no routine
        df2 = gdf[(gdf["rcount"] == 0) & (gdf["scount"] > 0)]
        if not df2.empty:
            arbpick(asosdb, sts.year, station, df2)
            continue

        print("Impossible Edge Case?")
        print(station)
        print(gdf)


if __name__ == "__main__":
    main(sys.argv)
