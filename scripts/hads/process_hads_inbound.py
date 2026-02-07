"""Moved staged SHEF data into long term tables.

Note, we do not want to do TRUNCATE here to do ugly locking that happens and
which can jam things up badly when we are doing upgrades, etc.

We want to over-write previous entries so to allow for corrections to work.
We assume that newer data is better :/

called from RUN_10MIN.sh
"""

import sys
from datetime import datetime, timezone

import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.reference import ISO8601
from pyiem.util import get_properties, logger, set_property, utc
from sqlalchemy.engine import Connection
from tqdm import tqdm

LOG = logger()
PROPERTY_NAME = "hads2archive_last"


@with_sqlalchemy_conn("hads")
def main(conn: Connection | None = None):
    """Do things"""
    updated_start = datetime.strptime(
        get_properties().get(PROPERTY_NAME, "2002-01-01T00:00:00Z"),
        ISO8601,
    ).replace(tzinfo=timezone.utc)
    updated_end = utc()
    set_property(PROPERTY_NAME, updated_end.strftime(ISO8601))
    nt = NetworkTable("ISUSM", only_online=False)
    # Sometimes we get old data that should not be in the database.
    obs = pd.read_sql(
        sql_helper("""
        SELECT station, valid at time zone 'UTC' as v, key, value, depth,
        unit_convention, qualifier, dv_interval from raw_inbound
        WHERE valid > '2002-01-01' and updated >= :sts and updated < :ets
        and not (station = Any(:stations))
        order by station asc, updated asc
    """),
        conn,
        index_col=None,
        parse_dates="v",
        params={
            "sts": updated_start,
            "ets": updated_end,
            "stations": list(nt.sts.keys()),
        },
    )
    LOG.info(
        "processing %s rows updated %s->%s",
        len(obs.index),
        updated_start,
        updated_end,
    )
    obs["v"] = obs["v"].dt.tz_localize(timezone.utc)
    obs["dv_interval"] = pd.to_timedelta(obs["dv_interval"])
    updates = 0
    inserts = 0
    duplicates = 0
    deletes = 0
    quiet = not sys.stdout.isatty()
    progress = tqdm(
        obs.itertuples(index=False),
        total=obs.shape[0],
        disable=quiet,
    )
    for row in progress:
        progress.set_description(
            f"Upd: {updates} Ins: {inserts} Dups: {duplicates} Del: {deletes}"
        )
        table = f"raw{row.v:%Y_%m}"
        dv_interval = None if pd.isna(row.dv_interval) else row.dv_interval
        depth = None if pd.isna(row.depth) else int(row.depth)
        value = None if pd.isna(row.value) else row.value
        # Sigh, we are doing so much dup data that we want to avoid
        # needless MVCC database updates
        res = conn.execute(
            sql_helper(
                """
    select value, ctid,
    (
        (CAST(:value AS double precision) is null and value is null)
        or (
            CAST(:value AS double precision) is not null
            and value is not null
            and abs(value - CAST(:value AS double precision)) < 1e-3
        )
    ) as is_duplicate
    from {table}  where
    station = :station and valid = :valid and key = :key
    and (depth IS NOT DISTINCT FROM :depth)
    and (unit_convention IS NOT DISTINCT FROM :unit_convention)
    and (qualifier IS NOT DISTINCT FROM :qualifier)
    and (dv_interval IS NOT DISTINCT FROM :dv_interval)
                """,
                table=table,
            ),
            {
                "station": row.station,
                "valid": row.v,
                "value": value,
                "key": row.key,
                "depth": depth,
                "unit_convention": row.unit_convention,
                "qualifier": row.qualifier,
                "dv_interval": dv_interval,
            },
        )
        if res.rowcount == 1 and res.fetchone()[2]:
            # No change needed
            duplicates += 1
            continue

        # Does this row already exist and careful about null comparisons
        res = conn.execute(
            sql_helper(
                """
    update {table} SET value = :value where
    station = :station and valid = :valid and key = :key
    and (depth IS NOT DISTINCT FROM :depth)
    and (unit_convention IS NOT DISTINCT FROM :unit_convention)
    and (qualifier IS NOT DISTINCT FROM :qualifier)
    and (dv_interval IS NOT DISTINCT FROM :dv_interval) returning ctid
                """,
                table=table,
            ),
            {
                "station": row.station,
                "valid": row.v,
                "value": value,
                "key": row.key,
                "depth": depth,
                "unit_convention": row.unit_convention,
                "qualifier": row.qualifier,
                "dv_interval": dv_interval,
            },
        )
        if res.rowcount > 0:
            if res.rowcount > 1:
                if not quiet:
                    progress.write(f"del {res.rowcount} dup entries {row}")
                # Delete 'em, except the last one :/
                ctids = [r[0] for r in res.fetchall()]
                # Let index help with query perf
                res = conn.execute(
                    sql_helper(
                        """
    DELETE FROM {table} where station = :station and valid = :valid and
    ctid = ANY(:ctids)""",
                        table=table,
                    ),
                    {
                        "ctids": ctids[:-1],
                        "station": row.station,
                        "valid": row.v,
                    },
                )
                deletes += res.rowcount
            updates += 1
            if updates % 1_000 == 0:
                conn.commit()
            continue
        inserts += 1
        if inserts % 1_000 == 0:
            conn.commit()
        conn.execute(
            sql_helper(
                """
    INSERT into {table}(station, valid, key, value, depth, unit_convention,
    qualifier, dv_interval) VALUES (:station, :valid, :key, :value,
    :depth, :unit_convention, :qualifier, :dv_interval)
                """,
                table=table,
            ),
            {
                "station": row.station,
                "valid": row.v,
                "key": row.key,
                "value": value,
                "depth": depth,
                "unit_convention": row.unit_convention,
                "qualifier": row.qualifier,
                "dv_interval": dv_interval,
            },
        )
    lglvl = LOG.warning if 0 in [updates, inserts] else LOG.info
    lglvl(
        "Updated %s rows, inserted %s row, %s dbdups, %s deletes",
        updates,
        inserts,
        duplicates,
        deletes,
    )
    res = conn.execute(
        sql_helper(
            "delete from raw_inbound where updated >= :sts and updated < :ets"
        ),
        {"sts": updated_start, "ets": updated_end},
    )
    LOG.info("removed %s inbound rows", res.rowcount)
    conn.commit()


if __name__ == "__main__":
    main()
