"""Compute hourly precip totals from the HADS/DCP sites.

hads=# select key, count(*), max(value) from raw2026_01
where substr(key, 1, 2) in ('PP', 'PC', 'PR') group by key order by count desc;

   key   |  count   |   max
 PCIRGZZ | 13575120 |  129400  Instantaneous accumulation, ~easy
 PPHRGZZ |  4179366 |  114636  Explcity hourly, good too
 PCIRRZZ |  2039035 |     723  Instantaneous accumulation, ~easy
 PPERGZZ |  1302182 |  1194.6  5 minute precip total, can we avoid?
 PPURRZZ |   658408 | 1121.61  1 minute, can we avoid?
 PPHR3ZZ |   641496 |  394.12  Explcit hourly
 PPHRZZZ |   629107 |    10.9

---> The database storage is for the hour the precip fell!

Run from RUN_20_AFTER.sh for previous hour

"""

from datetime import datetime, timedelta, timezone

import click
import numpy as np
import pandas as pd
from pyiem.database import (
    sql_helper,
    with_sqlalchemy_conn,
)
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()


@with_sqlalchemy_conn("mesosite")
def build_metadata(conn: Connection | None = None) -> pd.DataFrame:
    """Create the necessary metadata to do our work."""
    return pd.read_sql(
        sql_helper(
            """
        select iemid, id, tzname from stations where network ~* 'DCP'
        and tzname is not null order by id asc
        """
        ),
        conn,
        index_col="iemid",
    )


@with_sqlalchemy_conn("hads")
def build_obs(valid: datetime, conn: Connection | None = None) -> pd.DataFrame:
    """Figure out the obs that we have!"""
    # We don't want PPH values valid at the valid time, that is the previous hr
    # Some stations have seconds values, le sigh
    # Some stations have multiple sensors
    return pd.read_sql(
        sql_helper(
            """
        select distinct station, valid, key, value, substr(key, 1, 3) as key3,
        extract(minute from valid) as minute,
        substr(key, 4, 2) as sensor
        from {table} WHERE
        (
         (substr(key, 1, 3) = 'PPH' and valid > :sts and valid <= :ets) or
         (substr(key, 1, 3) = 'PCI' and valid >= :sts and valid <= :ets)
        ) and value >= 0 and unit_convention = 'E'
        ORDER by station asc, valid asc
        """,
            table=f"raw{valid:%Y}",
        ),
        conn,
        params={"sts": valid, "ets": valid + timedelta(minutes=61)},
        index_col=None,
    )


def set_value(
    conn: Connection,
    valid: datetime,
    hourlydf: pd.DataFrame,
    iemid: int,
    value: float,
):
    """Set the database value, maybe."""
    # Sanity check
    if value < 0 or value > 10:
        return
    params = {"iemid": iemid, "value": value, "valid": valid}
    if iemid in hourlydf.index:
        prev = float(hourlydf.at[iemid, "phour"])
        if np.isclose(prev, value):
            return
        LOG.info("Updating iemid %s from %.2f to %.2f", iemid, prev, value)
        conn.execute(
            sql_helper(
                """
            UPDATE {table} SET phour = :value
            WHERE iemid = :iemid AND valid = :valid
            """,
                table=f"hourly_{valid:%Y}",
            ),
            params,
        )
        return
    conn.execute(
        sql_helper(
            """
        insert into {table} (iemid, valid, phour)
        values (:iemid, :valid, :value)
        """,
            table=f"hourly_{valid:%Y}",
        ),
        params,
    )
    conn.commit()


@with_sqlalchemy_conn("iem")
def workflow(valid: datetime, conn: Connection | None = None):
    """Do the necessary work for this date"""
    metadf = build_metadata()
    LOG.info("Found %s DCP stations with valid tzname", len(metadf.index))

    # IMPORTANT valid is the hour of data we are processing for
    obsdf = build_obs(valid)
    LOG.info("Found %s HADS obs for %s", len(obsdf.index), valid)

    table = f"hourly_{valid:%Y}"
    hourlydf = pd.read_sql(
        sql_helper(
            "select iemid, phour from {table} where valid = :valid",
            table=table,
        ),
        conn,
        params={"valid": valid},
        index_col="iemid",
    )

    # Iterate over stations found
    counts = {
        "unknown_station": 0,
        "has_pph": 0,
        "has_pci": 0,
        "only_one_pci": 0,
        "multiple_sensors": 0,
        "unaccounted": 0,
    }
    for station, gdf in obsdf.groupby("station"):
        if station not in metadf["id"].values:
            counts["unknown_station"] += 1
            continue
        iemid = metadf.index[metadf["id"] == station][0]
        # Scenario 1, 1 entry of PPH, easy
        filtered = gdf[gdf["key3"] == "PPH"]
        if not filtered.empty:
            counts["has_pph"] += 1
            set_value(
                conn, valid, hourlydf, iemid, filtered["value"].values[0]
            )
            continue
        # Scenario 2, 2 entries of PCI at top of the hour
        filtered = gdf[(gdf["key3"] == "PCI") & (gdf["minute"] == 0)]
        if len(filtered.index) == 2:
            counts["has_pci"] += 1
            set_value(
                conn,
                valid,
                hourlydf,
                iemid,
                filtered["value"].values[-1] - filtered["value"].values[0],
            )
            continue
        # Scenario 3, only 1 PCI
        filtered = gdf[gdf["key3"] == "PCI"]
        if len(filtered.index) == 1:
            counts["only_one_pci"] += 1
            continue
        # Scenario 4, more than one sensor
        if gdf["sensor"].nunique() > 1:
            counts["multiple_sensors"] += 1
            continue
        counts["unaccounted"] += 1
        LOG.info("Unaccounted for scenario\n%s", gdf.to_markdown())
    LOG.info("Scenario counts: %s", counts)


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
def main(valid: datetime):
    """Do Something"""
    valid = valid.replace(tzinfo=timezone.utc)
    workflow(valid)


if __name__ == "__main__":
    main()
