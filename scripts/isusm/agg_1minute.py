"""
Need to do some custom 1 minute data aggregation to fill out hourly table.
"""
import datetime

import pandas as pd
import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, utc, logger

LOG = logger()


def do_updates(cursor, station, valid, row):
    """Make the updates happen, captain."""
    cursor.execute(
        """
        UPDATE sm_hourly SET
        tair_c_avg = %(tair_c_avg)s,
        tair_c_avg_qc = %(tair_c_avg)s,
        tsoil_c_avg = %(tsoil_c_avg)s,
        tsoil_c_avg_qc = %(tsoil_c_avg)s,
        calc_vwc_12_avg = %(calc_vwc_12_avg)s,
        calc_vwc_12_avg_qc = %(calc_vwc_12_avg)s,
        calc_vwc_24_avg = %(calc_vwc_24_avg)s,
        calc_vwc_24_avg_qc = %(calc_vwc_24_avg)s,
        calc_vwc_50_avg = %(calc_vwc_50_avg)s,
        calc_vwc_50_avg_qc = %(calc_vwc_50_avg)s,
        t12_c_avg = %(t12_c_avg)s,
        t12_c_avg_qc = %(t12_c_avg)s,
        t24_c_avg = %(t24_c_avg)s,
        t24_c_avg_qc = %(t24_c_avg)s,
        t50_c_avg = %(t50_c_avg)s,
        t50_c_avg_qc = %(t50_c_avg)s,
        obs_count = %(obs_count)s
        WHERE station = %(station)s and valid = %(hour)s
    """,
        row,
    )
    if cursor.rowcount == 0:
        LOG.debug("Updating %s %s resulted in 0 rows updated", station, valid)


def process(cursor, row):
    """Merge this row information into the database."""
    valid = row["hour"] + datetime.timedelta(hours=1)
    station = row["station"]
    cursor.execute(
        """
        SELECT obs_count from sm_hourly where station = %s and valid = %s
    """,
        (station, valid),
    )
    if cursor.rowcount == 1:
        current = cursor.fetchone()
        if current[0] == row["obs_count"]:
            LOG.debug(
                "%s %s obs_count %s matches", valid, station, row["obs_count"]
            )
            return
    elif cursor.rowcount == 0:
        # Need to create an entry
        cursor.execute(
            """
        INSERT into sm_hourly(station, valid, obs_count) values (%s, %s, 0)
        """,
            (station, valid),
        )
    do_updates(cursor, station, valid, row)


def main():
    """Go Main Go."""
    pgconn = get_dbconn("isuag")
    sts = utc() - datetime.timedelta(hours=36)
    sts = sts.replace(minute=0, second=0, microsecond=0)
    df = read_sql(
        """
    WITH data as (
        SELECT *,
        date_trunc('hour', valid - '1 minute'::interval) as hour,
        row_number() OVER (
            PARTITION by station,
            date_trunc('hour', valid - '1 minute'::interval)
            ORDER by valid DESC) as rn
        from sm_minute where valid >= %s
    )
    SELECT
    station, hour,
    count(*) as obs_count,
    max(case when rn = 1 then tair_c_avg else null end) as tair_c_avg,
    max(case when rn = 1 then tsoil_c_avg else null end) as tsoil_c_avg,
    max(case when rn = 1 then t12_c_avg else null end) as t12_c_avg,
    max(case when rn = 1 then t24_c_avg else null end) as t24_c_avg,
    max(case when rn = 1 then t50_c_avg else null end) as t50_c_avg,
    max(case when rn = 1 then calcVWC12_Avg else null end) as calc_vwc_12_avg,
    max(case when rn = 1 then calcVWC24_Avg else null end) as calc_vwc_24_avg,
    max(case when rn = 1 then calcVWC50_Avg else null end) as calc_vwc_50_avg
    from data GROUP by station, hour
    """,
        pgconn,
        params=(sts,),
        index_col=None,
    )
    # We want NaN values as None
    df = df.replace({np.nan: None})
    cursor = pgconn.cursor()
    for _, row in df.iterrows():
        process(cursor, row)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
