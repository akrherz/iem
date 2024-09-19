"""Hit up elevation REST service to compute a station elevation.

Called from SYNC_STATIONS.sh
"""

import time
from typing import Optional

import click
import httpx
from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def get_elevation(lon: float, lat: float) -> Optional[float]:
    """Use arcgisonline"""
    resp = httpx.get(
        f"https://api.opentopodata.org/v1/mapzen?locations={lat},{lon}",
        timeout=30,
    )
    if resp.status_code != 200:
        LOG.info("ERROR: %s", resp.status_code)
        return None
    return resp.json()["results"][0]["elevation"]


def workflow():
    """Our work"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()
    mcursor2 = pgconn.cursor()
    mcursor.execute(
        "SELECT network, ST_x(geom) as lon, ST_y(geom) as lat, elevation, id "
        "from stations WHERE (elevation < -990 or elevation is null)"
    )

    for row in mcursor:
        elev = row[3]
        lat = row[2]
        lon = row[1]
        sid = row[4]
        network = row[0]
        newelev = get_elevation(lon, lat)
        if newelev is None:
            print(f"Got None for {sid} {network}")
            continue

        print(f"{sid:7s} {network} OLD: {elev} NEW: {newelev:.3f}")
        mcursor2.execute(
            "UPDATE stations SET elevation = %s WHERE id = %s "
            "and network = %s",
            (newelev, sid, network),
        )
        time.sleep(2)

    mcursor2.close()
    pgconn.commit()


@click.command()
@click.option("--lon", type=float, help="Longitude")
@click.option("--lat", type=float, help="Latitude")
def main(lon: Optional[float], lat: Optional[float]):
    """Go Main Go"""
    if lon is not None and lat is not None:
        print(get_elevation(lon, lat))
        return
    workflow()


if __name__ == "__main__":
    main()
