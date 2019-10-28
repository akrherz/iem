"""Cut down the number of HML forecasts stored

Suspicion is that do to retrans, etc, there are lots of dups in the HML
database.  So this attempts to de-dup them.
"""
from __future__ import print_function
import sys
import datetime

import pytz
from pyiem.util import get_dbconn


def workflow(ts):
    """Deduplicate this timestep"""
    pgconn = get_dbconn("hads")
    cursor = pgconn.cursor()
    table = "hml_forecast_data_%s" % (ts.year,)
    cursor.execute(
        """
    with data as (
        select id, station, generationtime, issued,
    rank() OVER (PARTITION by station, issued ORDER by generationtime DESC),
        forecast_sts, forecast_ets from hml_forecast where
        issued >= %s and issued < %s)
    DELETE from """
        + table
        + """ where hml_forecast_id in
        (select id from data where rank > 1)
        """,
        (ts, ts + datetime.timedelta(days=1)),
    )
    print(
        ("dedup_hml_forecasts removed %s rows on %s for %s")
        % (cursor.rowcount, table, ts.strftime("%Y-%m-%d"))
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
        (ts, ts + datetime.timedelta(days=1)),
    )
    print(
        ("dedup_hml_forecasts removed %s rows on %s for %s")
        % (cursor.rowcount, "hml_forecast", ts.strftime("%Y-%m-%d"))
    )
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go Main Go"""
    if len(argv) != 4:
        ts = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    else:
        ts = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]))
    ts = ts.replace(tzinfo=pytz.utc)
    workflow(ts)


if __name__ == "__main__":
    main(sys.argv)
