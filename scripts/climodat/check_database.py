"""Rectify climodat database entries."""
from io import StringIO
import sys

import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, get_dbconnstr, logger

LOG = logger()


def main(argv):
    """Go Main"""
    state = argv[1]
    nt = NetworkTable(f"{state}CLIMATE", only_online=False)
    pgconn = get_dbconn("coop")
    df = pd.read_sql(
        f"SELECT station, year, day from alldata_{state} "
        "ORDER by station, day",
        get_dbconnstr("coop"),
        index_col=None,
    )

    for station, gdf in df.groupby("station"):
        if station not in nt.sts:
            LOG.info(
                "station: %s is unknown to %sCLIMATE, skip", station, state
            )
            continue
        # Make sure that our data archive starts on the first of a month
        minday = gdf["day"].min().replace(day=1)
        missing = pd.date_range(minday, gdf["day"].max()).difference(
            gdf["day"]
        )
        if missing.empty:
            continue
        LOG.warning(
            "station: %s, missing: %s [%s - %s] has:%s days",
            station,
            len(missing),
            missing.min().date(),
            missing.max().date(),
            len(gdf.index),
        )

        sio = StringIO()
        for day in missing:
            sio.write(f"{station},{day},{day:%m%d},{day:%Y},{day:%m}\n")
        sio.seek(0)
        cursor = pgconn.cursor()
        cursor.copy_from(
            sio,
            f"alldata_{state.lower()}",
            columns=("station", "day", "sday", "year", "month"),
            sep=",",
        )
        del sio
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
