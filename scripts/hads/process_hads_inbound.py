"""The pyWWA shef_parser dumps raw data into the raw_inbound table, this
script sorts through that mess and files it away into the longterm storage
tables.
"""
from __future__ import print_function

import pytz
from pyiem.util import get_dbconn


def main():
    """ Do things """
    pgconn = get_dbconn("hads")
    cursor2 = pgconn.cursor()
    cursor = pgconn.cursor()
    cursor.execute(
        """
        INSERT into raw_inbound_tmp
        SELECT distinct station, valid,
        key, value from raw_inbound
    """
    )
    cursor.execute("TRUNCATE raw_inbound")
    cursor.close()
    pgconn.commit()
    cursor = pgconn.cursor()
    cursor.execute(
        """
        SELECT station, valid at time zone 'UTC',
        key, value from raw_inbound_tmp
    """
    )
    for row in cursor:
        table = "raw%s" % (row[1].strftime("%Y_%m"),)
        ts = row[1].replace(tzinfo=pytz.utc)
        cursor2.execute(
            """
            INSERT into """
            + table
            + """
            (station, valid, key, value) VALUES (%s, %s, %s, %s)
        """,
            [row[0], ts, row[2], row[3]],
        )
    if cursor.rowcount == 0:
        print("process_hads_inbound.py found no data to insert...")
    cursor.execute("TRUNCATE raw_inbound_tmp")
    cursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
