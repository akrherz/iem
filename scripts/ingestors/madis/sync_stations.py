"""Compare IEM station metadata with what current MADIS netcdf has."""

import sys
import warnings

import click
from netCDF4 import chartostring
from pyiem.database import get_dbconn
from pyiem.util import ncopen

sys.path.insert(0, ".")
from to_iemaccess import LOG, provider2network  # skipcq

warnings.filterwarnings("ignore", category=DeprecationWarning)


@click.command()
@click.option("--filename", help="Path to MADIS netcdf file", required=True)
def main(filename: str):
    """Go Main Go"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()

    with ncopen(filename) as nc:
        stations = chartostring(nc.variables["stationId"][:])
        try:
            names = chartostring(nc.variables["stationName"][:])
        except UnicodeDecodeError:
            LOG.info("Falling back to bytes and manual name decode")
            names = chartostring(
                nc.variables["stationName"][:], "bytes"
            ).tolist()
            for i, name in enumerate(names):
                try:
                    names[i] = str(name.decode("utf-8"))
                except UnicodeDecodeError:
                    names[i] = ""
        providers = chartostring(nc.variables["dataProvider"][:])
        latitudes = nc.variables["latitude"][:]
        longitudes = nc.variables["longitude"][:]
    for recnum, provider in enumerate(providers):
        name = names[recnum].replace(",", " ")
        network = provider2network(provider, name)
        if network is None or network in ["IA_RWIS", "US_RWIS"]:
            continue
        stid = stations[recnum]
        mcursor.execute(
            "SELECT st_x(geom), st_y(geom), name from stations "
            "where id = %s and network = %s",
            (stid, network),
        )
        lon = float(longitudes[recnum])
        lat = float(latitudes[recnum])
        if mcursor.rowcount == 0:
            # Remove extraneous stuff in the name
            pos = name.find("   ")
            if pos > 0:
                name = name[:pos]
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
        (olon, olat, oname) = mcursor.fetchone()
        if oname == "":
            LOG.info("Updating name[%s] for %s %s", name, stid, network)
            mcursor.execute(
                "UPDATE stations SET name = %s WHERE id = %s and network = %s",
                (name, stid, network),
            )
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
