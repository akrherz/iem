"""Computes the Climatology and fills out the table!

Run for a previous date from RUN_2AM.sh
"""

import datetime
import sys

from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable
from pyiem.reference import state_names
from pyiem.util import logger

LOG = logger()

THISYEAR = datetime.date.today().year
META = {
    "climate51": {
        "sts": datetime.datetime(1951, 1, 1),
        "ets": datetime.datetime(THISYEAR, 1, 1),
    },
    "climate71": {
        "sts": datetime.datetime(1971, 1, 1),
        "ets": datetime.datetime(2001, 1, 1),
    },
    "climate": {
        "sts": datetime.datetime(1893, 1, 1),
        "ets": datetime.datetime(THISYEAR, 1, 1),
    },
    "climate81": {
        "sts": datetime.datetime(1981, 1, 1),
        "ets": datetime.datetime(2011, 1, 1),
    },
}


def daily_averages(table, ts):
    """
    Compute and Save the simple daily averages
    """
    pgconn, cursor = get_dbconnc("coop")
    sday_limiter = ""
    day_limiter = ""
    if ts is not None:
        sday_limiter = f" and sday = '{ts:%m%d}' "
        day_limiter = f" and valid = '2000-{ts:%m-%d}' "
    for st in state_names:
        nt = NetworkTable(f"{st}CLIMATE")
        if not nt.sts:
            LOG.info("Skipping %s as it has no stations", st)
            continue
        LOG.info("Computing Daily Averages for state: %s", st)
        cursor.execute(
            f"DELETE from {table} WHERE substr(station, 1, 2) = %s "
            f"{day_limiter}",
            (st,),
        )
        LOG.info("    removed %s rows from %s", cursor.rowcount, table)
        cursor.execute(
            f"""
    INSERT into {table} (station, valid, high, low,
        max_high, min_high,
        max_low, min_low,
        max_precip, precip,
        snow, years,
        gdd32, gdd41, gdd46, gdd48, gdd50, gdd51, gdd52,
        sdd86, hdd65, cdd65, max_range,
        min_range, srad)
    (SELECT station, ('2000-'|| to_char(day, 'MM-DD'))::date as d,
    avg(high) as avg_high, avg(low) as avg_low,
    max(high) as max_high, min(high) as min_high,
    max(low) as max_low, min(low) as min_low,
    max(precip) as max_precip, avg(precip) as precip,
    avg(snow) as snow, count(*) as years,
    avg(gddxx(32, 86, high, low)) as gdd32,
    avg(gddxx(41, 86, high, low)) as gdd41,
    avg(gddxx(46, 86, high, low)) as gdd46,
    avg(gddxx(48, 86, high, low)) as gdd48,
    avg(gddxx(50, 86, high, low)) as gdd50,
    avg(gddxx(51, 86, high, low)) as gdd51,
    avg(gddxx(52, 86, high, low)) as gdd52,
    avg( sdd86(high,low) ) as sdd86,
    avg( hdd65(high,low) ) as hdd65,
    avg(cdd65(high,low)) as cdd65,
    max( high - low) as max_range, min(high - low) as min_range,
    avg(merra_srad) as srad
    from alldata_{st} WHERE day >= %s and day < %s and
    precip is not null and high is not null and low is not null
    and station = ANY(%s) {sday_limiter}
    GROUP by d, station)""",
            (
                META[table]["sts"].strftime("%Y-%m-%d"),
                META[table]["ets"].strftime("%Y-%m-%d"),
                list(nt.sts.keys()),
            ),
        )
        LOG.info("    added %s rows to %s", cursor.rowcount, table)
    cursor.close()
    pgconn.commit()


def do_date(ccursor2, table, row, col, agg_col):
    """Process date"""
    ccursor2.execute(
        f"""
        SELECT year from alldata_{row['station'][:2]} where station = %s and
        abs({col} - {row[agg_col]}) < 0.001 and
        sday = %s and day >= %s and day < %s ORDER by year ASC
    """,
        (
            row["station"],
            row["valid"].strftime("%m%d"),
            META[table]["sts"],
            META[table]["ets"],
        ),
    )
    years = [row2["year"] for row2 in ccursor2]
    if not years:
        LOG.info(
            "None %s %s %s %s %s",
            row["station"],
            row["valid"],
            row[agg_col],
            col,
            agg_col,
        )
    return years


def set_daily_extremes(table, ts):
    """Set the extremes on a given table"""
    pgconn, cursor = get_dbconnc("coop")
    sday_limiter = ""
    if ts is not None:
        sday_limiter = f" and valid = '2000-{ts:%m-%d}' "
    cursor.execute(
        f"""
        SELECT * from {table} WHERE max_high_yr is null and
        max_high is not null
        and min_high_yr is null and min_high is not null
        and max_low_yr is null and max_low is not null
        and min_low_yr is null and min_low is not null {sday_limiter}
        """
    )
    ccursor2 = pgconn.cursor()
    cnt = 0
    for row in cursor:
        data = {}
        data["max_high_yr"] = do_date(ccursor2, table, row, "high", "max_high")
        data["min_high_yr"] = do_date(ccursor2, table, row, "high", "min_high")
        data["max_low_yr"] = do_date(ccursor2, table, row, "low", "max_low")
        data["min_low_yr"] = do_date(ccursor2, table, row, "low", "min_low")
        data["max_precip_yr"] = do_date(
            ccursor2, table, row, "precip", "max_precip"
        )
        ccursor2.execute(
            f"""
            UPDATE {table} SET max_high_yr = %s, min_high_yr = %s,
            max_low_yr = %s, min_low_yr = %s, max_precip_yr = %s
            WHERE station = %s and valid = %s
        """,
            (
                data["max_high_yr"],
                data["min_high_yr"],
                data["max_low_yr"],
                data["min_low_yr"],
                data["max_precip_yr"],
                row["station"],
                row["valid"],
            ),
        )
        cnt += 1
        if cnt % 1000 == 0:
            ccursor2.close()
            pgconn.commit()
            ccursor2 = pgconn.cursor()
    ccursor2.close()
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go Main Go"""
    ts = None
    if len(argv) == 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    for table in META:
        daily_averages(table, ts)
        set_daily_extremes(table, ts)


if __name__ == "__main__":
    main(sys.argv)
