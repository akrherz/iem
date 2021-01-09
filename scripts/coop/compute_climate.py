"""Computes the Climatology and fills out the table!"""
import datetime
import psycopg2.extras

from tqdm import tqdm
from pyiem.reference import state_names
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()
COOP = get_dbconn("coop")

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


def daily_averages(table):
    """
    Compute and Save the simple daily averages
    """
    for st in state_names:
        nt = NetworkTable("%sCLIMATE" % (st,))
        if not nt.sts:
            LOG.info("Skipping %s as it has no stations", st)
            continue
        LOG.info("Computing Daily Averages for state: %s", st)
        ccursor = COOP.cursor()
        ccursor.execute(
            f"DELETE from {table} WHERE substr(station, 1, 2) = %s", (st,)
        )
        LOG.info("    removed %s rows from %s", ccursor.rowcount, table)
        ccursor.execute(
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
    and station in %s
    GROUP by d, station)""",
            (
                META[table]["sts"].strftime("%Y-%m-%d"),
                META[table]["ets"].strftime("%Y-%m-%d"),
                tuple(nt.sts.keys()),
            ),
        )
        LOG.info("    added %s rows to %s", ccursor.rowcount, table)
        ccursor.close()
        COOP.commit()


def do_date(ccursor2, table, row, col, agg_col):
    """Process date"""
    ccursor2.execute(
        f"""
        SELECT year from alldata_{row['station'][:2]} where station = %s and
        {col} = {row[agg_col]} and sday = %s and day >= %s and day < %s
        ORDER by year ASC
    """,
        (
            row["station"],
            row["valid"].strftime("%m%d"),
            META[table]["sts"],
            META[table]["ets"],
        ),
    )
    row2 = ccursor2.fetchone()
    if row2 is None:
        LOG.info("None %s %s %s", row, col, agg_col)
        return "null"
    return row2[0]


def set_daily_extremes(table):
    """Set the extremes on a given table"""
    sql = """
    SELECT * from %s WHERE max_high_yr is null and max_high is not null
    and min_high_yr is null and min_high is not null
    and max_low_yr is null and max_low is not null
    and min_low_yr is null and min_low is not null
    """ % (
        table,
    )
    ccursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ccursor.execute(sql)
    ccursor2 = COOP.cursor()
    cnt = 0
    total = ccursor.rowcount
    for row in tqdm(ccursor, total=total):
        data = {}
        data["max_high_yr"] = do_date(ccursor2, table, row, "high", "max_high")
        data["min_high_yr"] = do_date(ccursor2, table, row, "high", "min_high")
        data["max_low_yr"] = do_date(ccursor2, table, row, "low", "max_low")
        data["min_low_yr"] = do_date(ccursor2, table, row, "low", "min_low")
        data["max_precip_yr"] = do_date(
            ccursor2, table, row, "precip", "max_precip"
        )
        ccursor2.execute(
            """
            UPDATE %s SET max_high_yr = %s, min_high_yr = %s,
            max_low_yr = %s, min_low_yr = %s, max_precip_yr = %s
            WHERE station = '%s' and valid = '%s'
        """
            % (
                table,
                data["max_high_yr"],
                data["min_high_yr"],
                data["max_low_yr"],
                data["min_low_yr"],
                data["max_precip_yr"],
                row["station"],
                row["valid"],
            )
        )
        cnt += 1
        if cnt % 1000 == 0:
            ccursor2.close()
            COOP.commit()
            ccursor2 = COOP.cursor()
    ccursor2.close()
    ccursor.close()
    COOP.commit()


def main():
    """Go Main Go"""
    for table in META:
        daily_averages(table)
        set_daily_extremes(table)


if __name__ == "__main__":
    main()
