"""Compute Shared Border Percentage for SBWs.

This was shunted from IEM Cow as it was too expensive to compute.

Run from RUN_5MIN.sh
"""

import click
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--year", type=int, default=2020, help="Year to compute for")
def main(year: int):
    """Go Main Go."""
    sbw_table = f"sbw_{year}"
    warning_table = f"warnings_{year}"
    # Flood Warnings FL/FA have ugly metadata between the tables :/
    # like
    sql = """
    WITH stormbased as (
        SELECT ctid, geom, wfo, eventid, phenomena, significance,
        least(polygon_begin, expire) as valid, status,
        ST_Length(st_transform(ST_exteriorring(ST_geometryn(
                        ST_multi(geom),1)), 2163)) as length
        from {sbw_table} WHERE shared_border_pct is null and
        phenomena in ('SV', 'TO', 'FF', 'MA', 'DS', 'SQ') limit 10000),
    countybased as (
        SELECT ST_Union(ST_ReducePrecision(u.simple_geom, 0.01)) as geom,
        s.ctid as s_ctid, w.wfo, w.phenomena, w.eventid, w.significance
        from {warning_table} w, ugcs u, stormbased s where
        s.wfo = w.wfo and s.eventid = w.eventid and s.phenomena = w.phenomena
        and s.significance = w.significance and s.valid >= w.issue and
        s.valid < w.expire + (case when s.status in ('EXP', 'CAN')
        then '1 minute'::interval else '0 minute'::interval end)
        and u.gid = w.gid and w.gid is not null
        GROUP by w.wfo, w.phenomena, w.eventid, w.significance, s.ctid),
    agg as (
        SELECT ST_SetSRID(ST_intersection(
                    ST_buffer(ST_exteriorring(
                        ST_geometryn(ST_multi(c.geom),1)),0.02),
                    ST_exteriorring(ST_geometryn(
                        ST_multi(s.geom),1))), 4326) as geo,
        s.ctid as s_ctid, s.length, s.eventid
        from stormbased s, countybased c WHERE
        s.ctid = c.s_ctid
    )

    SELECT sum(ST_Length(ST_transform(geo,2163))) as shared_length,
    max(coalesce(length, 0)) as perimeter, s_ctid from agg GROUP by s_ctid
    """
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            sql_helper(sql, sbw_table=sbw_table, warning_table=warning_table)
        )
        LOG.info("Found %s entries to process for %s", res.rowcount, year)
        for row in res.mappings():
            value = min(row["shared_length"] / row["perimeter"] * 100.0, 100)
            conn.execute(
                sql_helper(
                    "update {sbw_table} SET "
                    "shared_border_pct = :value where ctid = :ctid",
                    sbw_table=sbw_table,
                ),
                {"value": value, "ctid": row["s_ctid"]},
            )
        conn.commit()


if __name__ == "__main__":
    main()
