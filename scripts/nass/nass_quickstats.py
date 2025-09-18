"""Dump NASS Quickstats to the IEM database.

Run from RUN_10_AFTER.sh at 3 PM each day."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
import httpx
import numpy as np
import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.util import get_properties, logger

LOG = logger()
PROPS = get_properties()
TOPICS = [
    {"commodity_desc": "CORN", "statisticcat_desc": "PROGRESS"},
    {"commodity_desc": "SOYBEANS", "statisticcat_desc": "PROGRESS"},
    {"commodity_desc": "CORN", "statisticcat_desc": "YIELD"},
    {"commodity_desc": "SOYBEANS", "statisticcat_desc": "YIELD"},
    {"commodity_desc": "CORN", "statisticcat_desc": "CONDITION"},
    {"commodity_desc": "SOYBEANS", "statisticcat_desc": "CONDITION"},
    {"commodity_desc": "SOIL", "statisticcat_desc": "MOISTURE"},
    {"commodity_desc": "FIELDWORK", "statisticcat_desc": "DAYS SUITABLE"},
]
SERVICE = "https://quickstats.nass.usda.gov/api/api_GET/"


def get_df(year, sts, topic):
    """Figure out the data we need."""
    params = {
        "key": PROPS["usda.quickstats.key"],
        "format": "JSON",
        "program_desc": "SURVEY",
        "sector_desc": "CROPS",
    }
    if year is not None:
        params["year"] = year
    if sts is not None:
        params["load_time__GE"] = sts.strftime("%Y-%m-%d %H:%M:%S")
    params.update(topic)
    try:
        resp = httpx.get(SERVICE, params=params, timeout=300)
        resp.raise_for_status()
    except Exception as exp:
        LOG.warning("Error fetching NASS data: %s", exp)
        return None
    data = resp.json()
    return pd.DataFrame(data["data"])


def process(df):
    """Do some work"""
    # Try to get a number
    df["num_value"] = pd.to_numeric(df["Value"], errors="coerce")
    # Get load_time in proper order
    df["load_time"] = pd.to_datetime(
        df["load_time"].str.slice(0, 19), format="%Y-%m-%d %H:%M:%S"
    ).dt.tz_localize(ZoneInfo("America/New_York"))
    df = df.replace({np.nan: None, "": None})
    pgconn, cursor = get_dbconnc("coop")
    deleted = 0
    inserted = 0
    dups = 0
    for _, row in df.iterrows():
        # Ignore duplicated data like CONDITION, 5 YEAR AVG
        if row["statisticcat_desc"].find("YEAR") > 0:
            continue
        # fix SQL comparator
        cc = "is not distinct from" if row["week_ending"] is None else "="
        cf = "is not distinct from" if row["county_ansi"] is None else "="
        # Uniqueness by short_desc, year, state_alpha, week_ending
        cursor.execute(
            "SELECT load_time from nass_quickstats where year = %s "
            "and short_desc = %s and state_alpha = %s "
            f"and week_ending {cc} %s and freq_desc = %s and "
            f"county_ansi {cf} %s",
            (
                row["year"],
                row["short_desc"],
                row["state_alpha"],
                row["week_ending"],
                row["freq_desc"],
                row["county_ansi"],
            ),
        )
        if cursor.rowcount > 0:
            lt = cursor.fetchone()["load_time"]
            if lt == row["load_time"].to_pydatetime():
                dups += 1
                continue
            cursor.execute(
                "DELETE from nass_quickstats where year = %s "
                "and short_desc = %s and "
                f"state_alpha = %s and week_ending {cc} %s and freq_desc = %s "
                f"and county_ansi {cf} %s",
                (
                    row["year"],
                    row["short_desc"],
                    row["state_alpha"],
                    row["week_ending"],
                    row["freq_desc"],
                    row["county_ansi"],
                ),
            )
            deleted += cursor.rowcount
        inserted += 1
        cursor.execute(
            """
            INSERT into nass_quickstats(
            short_desc,
            sector_desc,
            group_desc,
            commodity_desc,
            class_desc,
            prodn_practice_desc,
            util_practice_desc,
            statisticcat_desc,
            unit_desc,
            agg_level_desc,
            state_alpha,
            year,
            freq_desc,
            begin_code,
            end_code,
            week_ending,
            load_time,
            value,
            cv,
            county_ansi,
            num_value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row["short_desc"],
                row["sector_desc"],
                row["group_desc"],
                row["commodity_desc"],
                row["class_desc"],
                row["prodn_practice_desc"],
                row["util_practice_desc"],
                row["statisticcat_desc"],
                row["unit_desc"],
                row["agg_level_desc"],
                row["state_alpha"],
                row["year"],
                row["freq_desc"],
                row["begin_code"],
                row["end_code"],
                row["week_ending"],
                row["load_time"],
                row["Value"],
                row["CV (%)"],
                row["county_ansi"],
                row["num_value"],
            ),
        )
    cursor.close()
    pgconn.commit()
    LOG.warning("Del %s, Inserted %s, Dups %s rows", deleted, inserted, dups)


@click.command()
@click.option("--all", "rerun_all", is_flag=True, help="Re-run all data")
def main(rerun_all: bool):
    """Go Main Go"""
    # Figure out a load_time
    if rerun_all:
        LOG.info("Re-running all!")
        sts = None
        # Oh my cats
        years = range(1866, datetime.now().year + 1)
    else:
        years = [None]
        sts = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0
        )

    for year in years:
        for topic in TOPICS:
            df = get_df(year, sts, topic)
            if df is not None:
                process(df)


if __name__ == "__main__":
    main()
