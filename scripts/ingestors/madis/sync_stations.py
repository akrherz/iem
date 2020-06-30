"""
Extract station data from file and update any new stations we find, please
"""
import sys

from netCDF4 import chartostring
from pyiem.util import get_dbconn, ncopen


MY_PROVIDERS = ["KYTC-RWIS", "KYMN", "NEDOR", "MesoWest"]


def provider2network(p):
    """ Convert a MADIS network ID to one that I use, here in IEM land"""
    if p in ["KYMN"]:
        return p
    if len(p) == 5 or p in ["KYTC-RWIS", "NEDOR"]:
        if p[:2] == "IA":
            return None
        return "%s_RWIS" % (p[:2],)
    print("Unsure how to convert %s into a network" % (p,))
    return None


def main(argv):
    """Go Main Go"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()

    fn = argv[1]
    nc = ncopen(fn)

    stations = chartostring(nc.variables["stationId"][:])
    names = chartostring(nc.variables["stationName"][:])
    providers = chartostring(nc.variables["dataProvider"][:])
    latitudes = nc.variables["latitude"][:]
    longitudes = nc.variables["longitude"][:]
    elevations = nc.variables["elevation"][:]
    for recnum, provider in enumerate(providers):
        if not provider.endswith("DOT") and provider not in MY_PROVIDERS:
            continue
        stid = stations[recnum]
        # can't have commas in the name, sigh
        name = names[recnum].replace(",", " ")
        if provider == "MesoWest":
            # get the network from the last portion of the name
            network = name.split()[-1]
            if network != "VTWAC":
                continue
        else:
            network = provider2network(provider)
        if network is None:
            continue
        mcursor.execute(
            """
            SELECT * from stations where id = %s and network = %s
        """,
            (stid, network),
        )
        if mcursor.rowcount > 0:
            continue
        print("Adding network: %s station: %s %s" % (network, stid, name))
        sql = """
            INSERT into stations(id, network, synop, country, plot_name,
            name, state, elevation, online, geom, metasite)
            VALUES ('%s', '%s', 9999, 'US',
            '%s', '%s', '%s', %s, 't', 'SRID=4326;POINT(%s %s)', 'f')
        """ % (
            stid,
            network,
            name,
            name,
            network[:2],
            elevations[recnum],
            longitudes[recnum],
            latitudes[recnum],
        )
        mcursor.execute(sql)
    nc.close()
    mcursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main(sys.argv)
