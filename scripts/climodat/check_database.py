"""
Rectify climodat database entries.

called from RUN_CLIMODAT_STATE.sh
"""

from io import StringIO

import click
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--state")
def main(state):
    """Go Main"""
    nt = NetworkTable(f"{state}CLIMATE", only_online=False)
    pgconn = get_dbconn("coop")
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"SELECT station, year, day from alldata_{state} "
            "ORDER by station, day",
            conn,
            index_col=None,
        )

    for station, gdf in df.groupby("station"):
        if station not in nt.sts:
            LOG.warning(
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
        sql = (
            f"copy alldata_{state.lower()}(station, day, sday, year, month) "
            "from stdin with (delimiter ',')"
        )
        with cursor.copy(sql) as copy:
            copy.write(sio.read())
        del sio
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
