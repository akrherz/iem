"""Computes the Climatology and fills out the table!

Run for a previous date from RUN_2AM.sh
"""

from datetime import date, datetime
from typing import NamedTuple

import click
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.reference import state_names
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()

THISYEAR = date.today().year
META = {
    "climate51": {
        "sts": datetime(1951, 1, 1),
        "ets": datetime(THISYEAR, 1, 1),
    },
    "climate71": {
        "sts": datetime(1971, 1, 1),
        "ets": datetime(2001, 1, 1),
    },
    "climate": {
        "sts": datetime(1893, 1, 1),
        "ets": datetime(THISYEAR, 1, 1),
    },
    "climate81": {
        "sts": datetime(1981, 1, 1),
        "ets": datetime(2011, 1, 1),
    },
}


@with_sqlalchemy_conn("coop")
def daily_averages(
    table: str, ts: datetime | None, conn: Connection | None = None
):
    """
    Compute and Save the simple daily averages
    """
    params = {
        "sts": META[table]["sts"].strftime("%Y-%m-%d"),
        "ets": META[table]["ets"].strftime("%Y-%m-%d"),
    }
    sday_limiter = ""
    day_limiter = ""
    if ts is not None:
        params["sday"] = f"{ts:%m%d}"
        params["valid"] = f"2000-{ts:%m-%d}"
        sday_limiter = " and sday = :sday "
        day_limiter = " and valid = :valid "
    for st in state_names:
        nt = NetworkTable(f"{st}CLIMATE")
        if not nt.sts:
            LOG.info("Skipping %s as it has no stations", st)
            continue
        LOG.info("Computing Daily Averages for state: %s", st)
        params["state"] = st
        res = conn.execute(
            sql_helper(
                "DELETE from {table} WHERE substr(station, 1, 2) = :state "
                "{day_limiter}",
                day_limiter=day_limiter,
                table=table,
            ),
            params,
        )
        LOG.info("    removed %s rows from %s", res.rowcount, table)
        params["sids"] = list(nt.sts.keys())

        res = conn.execute(
            sql_helper(
                """
    INSERT into {table} (station, valid, high, low,
        max_high, min_high,
        max_low, min_low,
        max_precip, precip,
        snow, years,
        gdd32, gdd41, gdd46, gdd48, gdd50, gdd51, gdd52,
        sdd86, hdd65, cdd65, max_range,
        min_range, srad, sgdd32, sgdd50, sgdd52)
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
    avg(merra_srad) as srad,
    avg(gddxx(32, 86, era5land_soilt4_max, era5land_soilt4_min)) as sgdd32,
    avg(gddxx(50, 86, era5land_soilt4_max, era5land_soilt4_min)) as sgdd50,
    avg(gddxx(52, 86, era5land_soilt4_max, era5land_soilt4_min)) as sgdd52
    from {table_alldata} WHERE day >= :sts and day < :ets and
    precip is not null and high is not null and low is not null
    and station = ANY(:sids) {sday_limiter}
    GROUP by d, station)""",
                table=table,
                sday_limiter=sday_limiter,
                table_alldata=f"alldata_{st}",
            ),
            params,
        )
        LOG.info("    added %s rows to %s", res.rowcount, table)
        conn.commit()


def do_date(
    conn: Connection, table: str, row: NamedTuple, col: str, lookfor: float
):
    """Process date"""
    res = conn.execute(
        sql_helper(
            """
        SELECT year from {table} where station = :station and
        abs({col} - cast(:lookfor as real)) < 0.001 and
        sday = :sday and day >= :sts and day <= :ets
        ORDER by year ASC
    """,
            table=f"alldata_{row.station[:2].lower()}",
            col=col,
        ),
        {
            "station": row.station,
            "sday": row.valid.strftime("%m%d"),
            "sts": META[table]["sts"],
            "ets": META[table]["ets"],
            "lookfor": lookfor,
        },
    )
    years = [row2[0] for row2 in res]
    if not years:
        LOG.info(
            "None %s %s %s %s",
            row.station,
            row.valid,
            lookfor,
            col,
        )
    return years


@with_sqlalchemy_conn("coop")
def set_daily_extremes(table, ts, conn: Connection | None = None):
    """Set the extremes on a given table"""
    params = {}
    sday_limiter = ""
    if ts is not None:
        params["valid"] = f"2000-{ts:%m-%d}"
        sday_limiter = " and valid = :valid "
    climodf = pd.read_sql(
        sql_helper(
            """
        SELECT * from {table} WHERE max_high_yr is null and
        max_high is not null
        and min_high_yr is null and min_high is not null
        and max_low_yr is null and max_low is not null
        and min_low_yr is null and min_low is not null {sday_limiter}
        """,
            table=table,
            sday_limiter=sday_limiter,
        ),
        conn,
        params=params,
    )
    cnt = 0
    for row in climodf.itertuples():
        data = {}
        data["max_high_yr"] = do_date(conn, table, row, "high", row.max_high)
        data["min_high_yr"] = do_date(conn, table, row, "high", row.min_high)
        data["max_low_yr"] = do_date(conn, table, row, "low", row.max_low)
        data["min_low_yr"] = do_date(conn, table, row, "low", row.min_low)
        data["max_precip_yr"] = do_date(
            conn, table, row, "precip", row.max_precip
        )
        conn.execute(
            sql_helper(
                """
    UPDATE {table} SET max_high_yr = :max_high_yr, min_high_yr = :min_high_yr,
    max_low_yr = :max_low_yr, min_low_yr = :min_low_yr,
    max_precip_yr = :max_precip_yr
    WHERE station = :station and valid = :valid
        """,
                table=table,
            ),
            {
                "max_high_yr": data["max_high_yr"],
                "min_high_yr": data["min_high_yr"],
                "max_low_yr": data["max_low_yr"],
                "min_low_yr": data["min_low_yr"],
                "max_precip_yr": data["max_precip_yr"],
                "station": row.station,
                "valid": row.valid,
            },
        )
        cnt += 1
        if cnt % 1000 == 0:
            conn.commit()
    conn.commit()


@click.command()
@click.option("--date", "dt", help="Date to process", type=click.DateTime())
def main(dt: datetime | None):
    """Go Main Go"""
    if dt is not None:
        dt = dt.date()
    for table in META:
        daily_averages(table, dt)
        set_daily_extremes(table, dt)


if __name__ == "__main__":
    main()
