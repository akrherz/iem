"""Compare IEM station metadata with what current MADIS netcdf has."""

import sys
import warnings

import click
from netCDF4 import chartostring
from pyiem.database import get_dbconn
from pyiem.util import logger, ncopen

sys.path.insert(0, ".")
from to_iemaccess import provider2network  # noqa

warnings.filterwarnings("ignore", category=DeprecationWarning)
LOG = logger()


@click.command()
@click.option("--filename", help="Path to MADIS netcdf file", required=True)
def main(filename: str):
    """Go Main Go"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()

    with ncopen(filename) as nc:
        stations = chartostring(nc.variables["stationId"][:])
        names = chartostring(nc.variables["stationName"][:])
        providers = chartostring(nc.variables["dataProvider"][:])
        latitudes = nc.variables["latitude"][:]
        longitudes = nc.variables["longitude"][:]
    for recnum, provider in enumerate(providers):
        name = names[recnum].replace(",", " ")
        network = provider2network(provider, name)
        if network is None or network == "IA_RWIS":
            continue
        stid = stations[recnum]
        mcursor.execute(
            "SELECT st_x(geom), st_y(geom) from stations "
            "where id = %s and network = %s",
            (stid, network),
        )
        lon = float(longitudes[recnum])
        lat = float(latitudes[recnum])
        if mcursor.rowcount == 0:
            LOG.warning("Add network: %s station: %s %s", network, stid, name)
            mcursor.execute(
                "INSERT into stations(id, network, synop, country, plot_name, "
                "name, state, online, geom, metasite) "
                "VALUES (%s, %s, 9999, 'US', %s, %s, %s, 't', "
                "ST_POINT(%s, %s, 4326), 'f')",
                (stid, network, name, name, network[:2], lon, lat),
            )
            continue
        # Compare location
        (olon, olat) = mcursor.fetchone()
        distance = ((olon - lon) ** 2 + (olat - lat) ** 2) ** 0.5
        if distance < 0.001:
            continue
        LOG.warning(
            "move %s %s dist: %s lon: %s -> %s lat: %s -> %s",
            stid,
            network,
            distance,
            olon,
            lon,
            olat,
            lat,
        )
        mcursor.execute(
            "UPDATE stations SET geom = ST_POINT(%s, %s, 4326) WHERE "
            "id = %s and network = %s",
            (lon, lat, stid, network),
        )

    mcursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
