"""
Assign a climate site to each site in the mesosite database, within reason
"""

import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()


@with_sqlalchemy_conn("mesosite")
def workflow(col: str, conn: Connection | None = None):
    """Query out all sites with a null climate_site"""
    sl = (
        "state is not null"
        if col != "climate_site"
        else "state != ANY(:states)"
    )
    updates = pd.read_sql(
        sql_helper(
            """
        SELECT id, geom, state, iemid, network,
        ST_x(geom) as lon, ST_y(geom) as lat
        from stations WHERE {col}
        IS NULL and country = 'US' and {sl}
        """,
            col=col,
            sl=sl,
        ),
        conn,
        params={
            "states": "PU P1 P2 P3 P4 P5".split(),
        },
        index_col="iemid",
    )
    LOG.info("Found %s stations needing update for %s", len(updates), col)
    for iemid, row in updates.iterrows():
        params = {
            "lon": row["lon"],
            "lat": row["lat"],
            "clnetwork": "NCDC81" if col == "ncdc81" else "NCEI91",
        }
        # Find the closest site
        if col == "climate_site":
            # Find the closest site that we have data in ncdc_climate71
            # which implies a valid climate_site entry already, chicken/egg
            sql = sql_helper("""
                select id,
                ST_Distance(geom, ST_Point(:lon, :lat, 4326)) as dist
                from stations where
                id in (select distinct climate_site from stations)
                ORDER by dist asc
                """)
        else:
            sql = sql_helper(
                "select id from stations WHERE network = :clnetwork "
                "ORDER by ST_distance(geom, ST_Point(:lon, :lat, 4326)) "
                "ASC LIMIT 1"
            )
        res = conn.execute(sql, params)
        if res.rowcount == 0:
            LOG.info("Could not find any %s sites for: %s", col, iemid)
            continue
        row2 = res.mappings().fetchone()
        conn.execute(
            sql_helper(
                "UPDATE stations SET {col} = :id WHERE iemid = :iemid", col=col
            ),
            {"id": row2["id"], "iemid": iemid},
        )
        LOG.info(
            "Set %s: %s for ID: %s[%s]",
            col,
            row2["id"],
            row["id"],
            row["network"],
        )
    conn.commit()


def main():
    """Go Main Go"""
    workflow("climate_site")
    workflow("ncdc81")
    workflow("ncei91")


if __name__ == "__main__":
    main()
