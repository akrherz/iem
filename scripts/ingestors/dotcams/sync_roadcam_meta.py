"""Sync the INTRANS metadata CSV."""

from datetime import datetime

import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()
SRC = "https://reactor-img.intrans.iastate.edu/images/camera_mapping.csv"


def process_date(text: str) -> pd.Timestamp | None:
    """Process an inconsistent string."""
    if text == "" or pd.isna(text):
        return None
    tokens = text.replace("-", "/").split("/")
    fmt = "%m/%d/%Y" if len(tokens[2]) == 4 else "%Y/%m/%d"
    return pd.Timestamp(datetime.strptime(text, fmt))


def process_group(
    gdf: pd.DataFrame,
    currentdf: pd.DataFrame,
    conn: Connection,
):
    """Do what we need to do."""
    for __, row in gdf.iterrows():
        date_added = process_date(row["DateAdded"])
        date_removed = process_date(row["DateRemoved"])
        currentrow = currentdf[currentdf["archive_begin"] == date_added]
        if currentrow.empty:
            LOG.warning("Adding %s", row.to_dict())
            conn.execute(
                sql_helper("""
    insert into dot_roadway_cams (device_id, name, archive_begin, archive_end,
    geom) values (:uid, :name, :date_added, :date_removed,
    ST_Point(:lon, :lat, 4326))
                           """),
                {
                    "uid": row["Id"],
                    "name": row["Name"],
                    "date_added": date_added,
                    "date_removed": date_removed,
                    "lon": row["Longitude"] / 10e7,
                    "lat": row["Latitude"] / 10e7,
                },
            )
            conn.commit()
            return


@with_sqlalchemy_conn("mesosite")
def main(conn: Connection | None = None) -> None:
    """Go Main Go."""
    current = pd.read_sql(
        sql_helper("""
            select *, st_x(geom) as lon, st_y(geom) as lat from
            dot_roadway_cams order by cam_id asc
                    """),
        conn,
        index_col="cam_id",
    )
    LOG.info("Fetched %s current records", len(current.index))
    upstream = pd.read_csv(SRC, dtype={"DateAdded": str, "DateRemoved": str})
    if len(upstream.index) < 1000:
        LOG.warning("Abort, found %s upstream records", len(upstream.index))
        return
    LOG.info("Fetched %s upstream records", len(upstream.index))
    for (uid, name), gdf in upstream.groupby(["Id", "Name"]):
        currentdf = current[
            (current["device_id"] == uid) & (current["name"] == name)
        ]
        process_group(gdf, currentdf, conn)


if __name__ == "__main__":
    main()
