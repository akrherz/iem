"""Dump NASS Quickstats to the IEM database.

Run from RUN_10_AFTER.sh at 3 PM each day."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
import httpx
import numpy as np
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import get_properties, logger
from sqlalchemy.engine import Connection

LOG = logger()
PROPS = get_properties()
TOPICS = [
    {"commodity_desc": "CORN", "statisticcat_desc": "PROGRESS"},
    {"commodity_desc": "SOYBEANS", "statisticcat_desc": "PROGRESS"},
    {"commodity_desc": "SORGHUM", "statisticcat_desc": "PROGRESS"},
    {"commodity_desc": "WHEAT", "statisticcat_desc": "PROGRESS"},
    {"commodity_desc": "CORN", "statisticcat_desc": "YIELD"},
    {"commodity_desc": "SOYBEANS", "statisticcat_desc": "YIELD"},
    {"commodity_desc": "SORGHUM", "statisticcat_desc": "YIELD"},
    {"commodity_desc": "WHEAT", "statisticcat_desc": "YIELD"},
    {"commodity_desc": "CORN", "statisticcat_desc": "CONDITION"},
    {"commodity_desc": "SOYBEANS", "statisticcat_desc": "CONDITION"},
    {"commodity_desc": "SORGHUM", "statisticcat_desc": "CONDITION"},
    {"commodity_desc": "WHEAT", "statisticcat_desc": "CONDITION"},
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
        # Shrug, getting a Bad Request when there is no data
        if resp.status_code == 400:
            return None
        resp.raise_for_status()
    except Exception as exp:
        LOG.warning("Error fetching NASS data: %s", exp)
        return None
    data = resp.json()
    return pd.DataFrame(data["data"])


@with_sqlalchemy_conn("coop")
def process(df: pd.DataFrame, conn: Connection | None = None):
    """Do some work"""
    # Try to get a number
    df["num_value"] = pd.to_numeric(df["Value"], errors="coerce")
    # Get load_time in proper order
    df["load_time"] = pd.to_datetime(
        df["load_time"].str.slice(0, 19), format="%Y-%m-%d %H:%M:%S"
    ).dt.tz_localize(ZoneInfo("America/New_York"))
    df = df.replace({np.nan: None, "": None})
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
        res = conn.execute(
            sql_helper(
                """
    SELECT load_time from nass_quickstats where year = :yr
    and short_desc = :sd and state_alpha = :sa
    and week_ending {cc} :we and freq_desc = :fd and
    county_ansi {cf} :ca
                       """,
                cc=cc,
                cf=cf,
            ),
            {
                "yr": row["year"],
                "sd": row["short_desc"],
                "sa": row["state_alpha"],
                "we": row["week_ending"],
                "fd": row["freq_desc"],
                "ca": row["county_ansi"],
            },
        )
        if res.rowcount > 0:
            lt = res.mappings().fetchone()["load_time"]
            if lt == row["load_time"].to_pydatetime():
                dups += 1
                continue
            conn.execute(
                sql_helper(
                    """
    DELETE from nass_quickstats where year = :yr
                and short_desc = :sd and state_alpha = :sa
                and week_ending {cc} :we and freq_desc = :fd
                and county_ansi {cf} :ca
                """,
                    cc=cc,
                    cf=cf,
                ),
                {
                    "yr": row["year"],
                    "sd": row["short_desc"],
                    "sa": row["state_alpha"],
                    "we": row["week_ending"],
                    "fd": row["freq_desc"],
                    "ca": row["county_ansi"],
                },
            )
            deleted += res.rowcount
        inserted += 1
        conn.execute(
            sql_helper("""
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
            num_value) VALUES (:p1, :p2, :p3, :p4, :p5, :p6, :p7, :p8, :p9,
            :p10, :p11, :p12, :p13, :p14, :p15, :p16, :p17, :p18, :p19, :p20,
            :p21)
            """),
            {
                "p1": row["short_desc"],
                "p2": row["sector_desc"],
                "p3": row["group_desc"],
                "p4": row["commodity_desc"],
                "p5": row["class_desc"],
                "p6": row["prodn_practice_desc"],
                "p7": row["util_practice_desc"],
                "p8": row["statisticcat_desc"],
                "p9": row["unit_desc"],
                "p10": row["agg_level_desc"],
                "p11": row["state_alpha"],
                "p12": row["year"],
                "p13": row["freq_desc"],
                "p14": row["begin_code"],
                "p15": row["end_code"],
                "p16": row["week_ending"],
                "p17": row["load_time"],
                "p18": row["Value"],
                "p19": row["CV (%)"],
                "p20": row["county_ansi"],
                "p21": row["num_value"],
            },
        )
    conn.commit()
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
