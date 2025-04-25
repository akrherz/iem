"""Update hourly precip tables.

For better or worse, we have a manual accounting of precipitation totals within
the database.  This updates those totals.

Called from RUN_10_AFTER.sh
"""

from datetime import datetime, timedelta, timezone

import click
from pyiem.database import get_dbconnc
from pyiem.util import utc


def update(icursor, iemid, valid, phour):
    """Update value."""
    icursor.execute(
        f"DELETE from hourly_{valid.year} WHERE valid = %s and iemid = %s",
        (valid, iemid),
    )
    icursor.execute(
        f"INSERT into hourly_{valid.year} (valid, phour, iemid) "
        "VALUES (%s, %s, %s)",
        (valid, phour, iemid),
    )


def archive(ts):
    """Reprocess an older date

    Currently, we only support the METAR database :(
    """
    asos, acursor = get_dbconnc("asos")
    acursor = asos.cursor()
    iem, icursor = get_dbconnc("iem")

    acursor.execute(
        f"""WITH data as (
        SELECT station, max(p01i) from t{ts.year}
        WHERE valid > %s and valid <= %s and p01i is not null
        GROUP by station)

    SELECT max, iemid from data d JOIN stations s on
    (d.station = s.id) WHERE s.network ~* 'ASOS'
    """,
        (ts, ts + timedelta(minutes=60)),
    )

    for row in acursor:
        update(icursor, row[1], ts, row[0])

    icursor.close()
    iem.commit()


def realtime(ts):
    """realtime"""
    pgconn, icursor = get_dbconnc("iem")
    acursor = pgconn.cursor()
    acursor.execute(
        """
        SELECT max(phour) as p, t.iemid
        from current_log c, stations t WHERE
        (valid - '1 minute'::interval) >= %s
        and (valid - '1 minute'::interval) < %s
        and phour >= 0 and c.iemid = t.iemid and t.network !~* 'DCP'
        GROUP by t.iemid
        """,
        (ts, ts + timedelta(minutes=60)),
    )
    for row in acursor:
        update(icursor, row["iemid"], ts, row["p"])

    pgconn.commit()
    pgconn.close()


@click.command()
@click.option("--valid", type=click.DateTime(), help="UTC Timestamp")
def main(valid: datetime | None):
    """Do things"""
    if valid:
        # Run for a custom hour
        archive(valid.replace(tzinfo=timezone.utc))
    else:
        # We run for the last hour
        ts = utc() - timedelta(hours=1)
        ts = ts.replace(minute=0, second=0, microsecond=0)
        realtime(ts)


if __name__ == "__main__":
    main()
