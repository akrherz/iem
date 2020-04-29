"""Update hourly precip tables.

For better or worse, we have a manual accounting of precipitation totals within
the database.  This updates those totals.
"""
import datetime
import sys

from pyiem.util import get_dbconn, utc


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
    asos = get_dbconn("asos", user="nobody")
    acursor = asos.cursor()
    iem = get_dbconn("iem")
    icursor = iem.cursor()

    acursor.execute(
        f"""WITH data as (
        SELECT station, max(p01i) from t{ts.year}
        WHERE valid > %s and valid <= %s and p01i is not null
        GROUP by station)

    SELECT max, iemid from data d JOIN stations s on
    (d.station = s.id) WHERE (s.network ~* 'ASOS' or s.network = 'AWOS')
    """,
        (ts, ts + datetime.timedelta(minutes=60)),
    )

    for row in acursor:
        update(icursor, row[1], ts, row[0])

    icursor.close()
    iem.commit()


def realtime(ts):
    """realtime"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()
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
        (ts, ts + datetime.timedelta(minutes=60)),
    )
    for row in acursor:
        update(icursor, row[1], ts, row[0])

    pgconn.commit()
    pgconn.close()


def main(argv):
    """Do things"""
    if len(argv) == 5:
        # Run for a custom hour
        ts = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
        archive(ts)
    else:
        # We run for the last hour
        ts = utc() - datetime.timedelta(hours=1)
        ts = ts.replace(minute=0, second=0, microsecond=0)
        realtime(ts)


if __name__ == "__main__":
    main(sys.argv)
