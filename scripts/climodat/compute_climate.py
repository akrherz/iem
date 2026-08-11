"""Computes the Climatology and fills out the table!

Run for a previous date from RUN_2AM.sh
"""

import sys
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.reference import TRACE_VALUE, state_names
from pyiem.util import logger
from sqlalchemy.engine import Connection
from tqdm import tqdm

LOG = logger()

THISYEAR = date.today().year
META = {
    "climate51": {
        "sts": date(1951, 1, 1),
        "ets": date(THISYEAR, 1, 1),
    },
    "climate71": {
        "sts": date(1971, 1, 1),
        "ets": date(2001, 1, 1),
    },
    "climate": {
        "sts": date(1893, 1, 1),
        "ets": date(THISYEAR + 1, 1, 1),
    },
    "climate81": {
        "sts": date(1981, 1, 1),
        "ets": date(2011, 1, 1),
    },
}


def r0(val: Any):
    """Round this to an int."""
    if pd.isna(val):
        return None
    return int(round(val, 0))


def r2(val: Any):
    """Round this to 2 decimal places."""
    if pd.isna(val):
        return None
    # Special hack here for Trace values
    if abs(val - TRACE_VALUE) < 0.00001:
        return TRACE_VALUE
    return round(val, 2)


def get_stat(
    statsdf: pd.DataFrame, varname: str, aggstat: str, func: Callable
):
    """The data may not exist, so alas."""
    try:
        val = func(statsdf[varname][aggstat])
        return val
    except KeyError:
        return None


def process_station(
    station: str,
    obsdf: pd.DataFrame,
    dt: date,
    table: str,
    conn: Connection,
):
    """Process a single station's data"""
    # Most things will get computed with this. This is a performance hotspot
    stats = obsdf[
        [
            "high",
            "low",
            "precip",
            "snow",
            "gdd50",
            "sdd86",
            "range",
            "hdd65",
            "gdd32",
            "gdd41",
            "gdd46",
            "gdd48",
            "gdd51",
            "gdd52",
            "cdd65",
            "era5land_srad",
            "sgdd32",
            "sgdd50",
            "sgdd52",
        ]
    ].describe(percentiles=[])
    params = {
        "station": station,
        "valid": dt,
        "high": get_stat(stats, "high", "mean", r0),
        "low": get_stat(stats, "low", "mean", r0),
        "precip": get_stat(stats, "precip", "mean", r2),
        "snow": get_stat(stats, "snow", "mean", r2),
        "max_high": get_stat(stats, "high", "max", r0),
        "max_low": get_stat(stats, "low", "max", r0),
        "min_high": get_stat(stats, "high", "min", r0),
        "min_low": get_stat(stats, "low", "min", r0),
        "max_precip": get_stat(stats, "precip", "max", r2),
        # One of these better work or we'll error below
        "years": (
            get_stat(stats, "high", "count", r0)
            or get_stat(stats, "precip", "count", r0)
            or get_stat(stats, "low", "count", r0)
        ),
        "gdd50": get_stat(stats, "gdd50", "mean", r2),
        "sdd86": get_stat(stats, "sdd86", "mean", r2),
        "max_range": get_stat(stats, "range", "max", r0),
        "min_range": get_stat(stats, "range", "min", r0),
        "hdd65": get_stat(stats, "hdd65", "mean", r2),
        "gdd32": get_stat(stats, "gdd32", "mean", r2),
        "gdd41": get_stat(stats, "gdd41", "mean", r2),
        "gdd46": get_stat(stats, "gdd46", "mean", r2),
        "gdd48": get_stat(stats, "gdd48", "mean", r2),
        "gdd51": get_stat(stats, "gdd51", "mean", r2),
        "gdd52": get_stat(stats, "gdd52", "mean", r2),
        "cdd65": get_stat(stats, "cdd65", "mean", r2),
        "srad": get_stat(stats, "era5land_srad", "mean", r2),
        "sgdd32": get_stat(stats, "sgdd32", "mean", r2),
        "sgdd50": get_stat(stats, "sgdd50", "mean", r2),
        "sgdd52": get_stat(stats, "sgdd52", "mean", r2),
        "max_high_yr": [],
        "max_low_yr": [],
        "min_high_yr": [],
        "min_low_yr": [],
        "max_precip_yr": [],
    }
    if not params["years"]:  # Ensure both not None and > 0
        LOG.info(
            "Station: %s has no data for %s[%s], skipping", station, dt, table
        )
        return
    for col in ["max_high", "max_low", "min_low", "min_high", "max_precip"]:
        if params[col] is not None:
            paramcol = f"{col}_yr"
            params[paramcol] = obsdf[obsdf[col.split("_")[1]] == params[col]][
                "year"
            ].to_list()

    # Remove the current datbase entry
    conn.execute(
        sql_helper(
            """
            delete from {table} where station = :station and valid = :valid
            """,
            table=table,
        ),
        {"station": station, "valid": dt},
    )

    # Here we go
    conn.execute(
        sql_helper(
            """
    insert into {table} (station, valid, high, low, precip, snow, max_high,
    max_low, min_high, min_low, max_precip, years, gdd50, sdd86, max_range,
    min_range, hdd65, gdd32, gdd41, gdd46, gdd48, gdd51, gdd52, cdd65, srad,
    max_high_yr, max_low_yr, min_high_yr, min_low_yr, max_precip_yr,
    sgdd32, sgdd50, sgdd52) values (
    :station, :valid, :high, :low, :precip, :snow, :max_high,
    :max_low, :min_high, :min_low, :max_precip, :years, :gdd50, :sdd86,
    :max_range, :min_range, :hdd65, :gdd32, :gdd41, :gdd46, :gdd48, :gdd51,
    :gdd52, :cdd65, :srad, :max_high_yr, :max_low_yr, :min_high_yr,
    :min_low_yr, :max_precip_yr, :sgdd32, :sgdd50, :sgdd52)
            """,
            table=table,
        ),
        params,
    )


def process(
    progress: tqdm,
    table: str,
    dt: date,
    obsdf: pd.DataFrame,
):
    """Do the processing work for this table and date,"""
    # Load up our climatology dataset.
    with get_sqlalchemy_conn("coop") as conn:
        for station, gdf in obsdf.groupby("station"):
            progress.set_description(f"{table} {station}")
            process_station(station, gdf, dt, table, conn)
        conn.commit()


@click.command()
@click.option(
    "--date",
    "dt",
    help="Date to process",
    type=click.DateTime(),
    required=True,
)
@click.option(
    "--state",
    "state_in",
    help="Run for just the given state abbreviation.",
    type=str,
    required=False,
)
def main(dt: datetime, state_in: str | None):
    """Go Main Go"""
    # Climate tables use dates during 2000, since it has a leap day
    dt = dt.date().replace(year=2000)
    is_interactive = sys.stdout.isatty()
    if state_in is not None:
        states = [state_in]
    else:
        states = state_names.keys()
    progress = tqdm(states, disable=not is_interactive)
    for state in progress:
        nt = NetworkTable(f"{state}CLIMATE")
        if not nt.sts:
            if is_interactive:
                progress.write(f"Skipping state: {state} as no stations")
            continue
        with get_sqlalchemy_conn("coop") as conn:
            obsdf = pd.read_sql(
                sql_helper(
                    """
    select *,
    gddxx(32, 86, high, low) as gdd32,
    gddxx(41, 86, high, low) as gdd41,
    gddxx(46, 86, high, low) as gdd46,
    gddxx(48, 86, high, low) as gdd48,
    gddxx(50, 86, high, low) as gdd50,
    gddxx(51, 86, high, low) as gdd51,
    gddxx(52, 86, high, low) as gdd52,
    sdd86(high, low) as sdd86,
    hdd65(high, low) as hdd65,
    cdd65(high, low) as cdd65,
    high - low as range,
    gddxx(32, 86, era5land_soilt4_max, era5land_soilt4_min) as sgdd32,
    gddxx(50, 86, era5land_soilt4_max, era5land_soilt4_min) as sgdd50,
    gddxx(52, 86, era5land_soilt4_max, era5land_soilt4_min) as sgdd52
    from {table} where sday = :sday order by station
        """,
                    table=f"alldata_{state.lower()}",
                ),
                conn,
                params={"sday": dt.strftime("%m%d")},
            )

        for table in META:
            obsdf_filtered = obsdf[
                (obsdf["day"] >= META[table]["sts"])
                & (obsdf["day"] < META[table]["ets"])
            ]
            if not obsdf_filtered.empty:
                process(progress, table, dt, obsdf_filtered)


if __name__ == "__main__":
    main()
