"""Sync CoCoRaHS station details.

Run from RUN_40_AFTER.sh
"""

from datetime import datetime
from io import StringIO

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import convert_value, logger
from sqlalchemy import text

LOG = logger()


@click.command()
@click.option("--newerthan", type=click.DateTime(), required=True)
def main(newerthan: datetime):
    """Go Main Go"""
    with get_sqlalchemy_conn("mesosite") as conn:
        current = pd.read_sql(
            text("""
    select id, name, st_x(geom) as lon, st_y(geom) as lat, elevation, iemid
    from stations where network ~* '_COCORAHS' order by id
            """),
            conn,
            index_col="id",
        )
    LOG.info("Found %s current COCORAHS stations", len(current.index))
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()

    url = (
        "http://data.cocorahs.org/cocorahs/export/exportstations.aspx?"
        "Format=CSV"
    )
    with StringIO() as sio:
        try:
            resp = httpx.get(url, timeout=30)
            resp.raise_for_status()
            sio.write(resp.text.replace(", ", ","))  # remove space after comma
        except Exception as exp:
            LOG.exception(exp)
            return
        sio.seek(0)
        upstream = pd.read_csv(sio).set_index("StationNumber")
    upstream["updated"] = pd.to_datetime(
        upstream["DateTimeStamp"], format="%Y-%m-%d %I:%M %p"
    )
    upstream = upstream[upstream["updated"] > newerthan]
    LOG.info("Found %s upstream COCORAHS stations", len(upstream.index))
    # We only want CoCoRaHS types
    upstream = upstream[upstream["StationType"] == "CoCoRaHS"]
    upstream["Latitude"] = pd.to_numeric(upstream["Latitude"], errors="coerce")
    upstream["Longitude"] = pd.to_numeric(
        upstream["Longitude"], errors="coerce"
    )

    for sid, row in upstream.iterrows():
        if (
            row["Latitude"] == 0
            or row["Longitude"] == 0
            or row["Elevation"] < -900
            or pd.isna(row["StationName"])
        ):
            continue
        network = f"{row['State']}_COCORAHS"
        sname = row["StationName"].strip().replace("'", " ")
        elevation = convert_value(row["Elevation"], "foot", "meter")
        dirty = False
        if sid not in current.index:
            state = None if sid[2] != "-" else sid[:2]
            country = {
                "BHS": "BH",
                "CAN": "CA",
            }.get(sid.split("-")[0], "US")
            mcursor.execute(
                """
                insert into stations(id, network, online, metasite, state,
                country) values
                (%s, %s, 't', 't', %s, %s) returning iemid
                """,
                (sid, network, state, country),
            )
            iemid = mcursor.fetchone()[0]
            dirty = True
        else:
            iemid = current.at[sid, "iemid"]
            if abs(current.at[sid, "elevation"] - elevation) > 3:
                dirty = True
            if abs(current.at[sid, "lat"] - row["Latitude"]) > 0.01:
                dirty = True
            if abs(current.at[sid, "lon"] - row["Longitude"]) > 0.01:
                dirty = True
            if current.at[sid, "name"] != sname:
                LOG.info(
                    "Station %s name changed from `%s` to `%s`",
                    sid,
                    current.at[sid, "name"],
                    sname,
                )
                dirty = True
        if not dirty:
            continue
        LOG.info("Updating %s", row)
        mcursor.execute(
            "UPDATE stations SET geom = ST_Point(%s, %s, 4326), wfo = null, "
            "elevation = %s, ugc_county = null, ugc_zone = null, "
            "ncdc81 = null, climate_site = null, ncei91 = null, name = %s, "
            "plot_name = %s WHERE iemid = %s",
            (
                row["Longitude"],
                row["Latitude"],
                elevation,
                sname,
                sname,
                iemid,
            ),
        )
        break

    mcursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
