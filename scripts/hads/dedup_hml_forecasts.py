"""Cut down the number of HML forecasts stored

Suspicion is that do to retrans, etc, there are lots of dups in the HML
database.  So this attempts to de-dup them.

Run from RUN_MIDNIGHT.sh for previous UTC date
"""

from datetime import datetime, timedelta, timezone

import click
from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def workflow(ts: datetime):
    """Deduplicate this timestep"""
    pgconn = get_dbconn("hml")
    cursor = pgconn.cursor()
    table = f"hml_forecast_data_{ts:%Y}"
    cursor.execute(
        f"""
    with data as (
        select id, station, generationtime, issued,
    rank() OVER (PARTITION by station, issued ORDER by generationtime DESC),
        forecast_sts, forecast_ets from hml_forecast where
        issued >= %s and issued < %s)
    DELETE from {table} where hml_forecast_id in
        (select id from data where rank > 1)
        """,
        (ts, ts + timedelta(days=1)),
    )
    LOG.info(
        "removed %s rows on %s for %s",
        cursor.rowcount,
        table,
        ts.strftime("%Y-%m-%d"),
    )
    cursor.execute(
        """
    with data as (
        select id, station, generationtime, issued,
    rank() OVER (PARTITION by station, issued ORDER by generationtime DESC),
        forecast_sts, forecast_ets from hml_forecast where
        issued >= %s and issued < %s)
    DELETE from hml_forecast where id in
        (select id from data where rank > 1)
    """,
        (ts, ts + timedelta(days=1)),
    )
    LOG.info(
        "dedup_hml_forecasts removed %s rows on %s for %s",
        cursor.rowcount,
        "hml_forecast",
        ts.strftime("%Y-%m-%d"),
    )
    cursor.close()
    pgconn.commit()


@click.command()
@click.option("--date", "dt", type=click.DateTime())
def main(dt: datetime):
    """Go Main Go"""
    dt = dt.replace(tzinfo=timezone.utc)
    workflow(dt)


if __name__ == "__main__":
    main()
