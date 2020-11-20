"""create initial database entries"""

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger
from pandas.io.sql import read_sql

LOG = logger()


def find_id(table, rid):
    """Find remote id"""
    for sid in table.sts:
        if rid == table.sts[sid]["remote_id"]:
            return sid
    return None


def main():
    """Go Main Go"""
    mesosite = get_dbconn("mesosite")
    cursor = mesosite.cursor()
    nt = NetworkTable("IA_RWIS")

    # Load up our current webcams
    df = read_sql(
        "SELECT cam, valid from camera_current where cam ~* 'IDOT'",
        mesosite,
        index_col="cam",
    )

    for cam in df.index.values:
        cursor.execute("SELECT * from webcams WHERE id = %s", (cam,))
        if cursor.rowcount > 0:
            continue

        rid = cam[6:8]
        nwsli = find_id(nt, int(rid))
        if nwsli is None:
            LOG.info("Failed to find remote_id: %s", rid)
            continue

        cursor.execute(
            "SELECT name, ST_x(geom) as lon, ST_y(geom) as lat "
            "from stations where id = %s",
            (nwsli,),
        )
        row = cursor.fetchone()
        lon = row[1]
        lat = row[2]
        name = row[0]
        LOG.info("Adding %s name [%s] lon [%s] lat [%s]", cam, name, lon, lat)
        cursor.execute(
            "insert into webcams (sts, id, name, pan0, online, network, "
            "geom, removed, state) values (now(), %s, %s, 0, 't', "
            "'IDOT', 'SRID=4326;POINT(%s %s)', 'f', 'IA')",
            (cam, name, lon, lat),
        )
    cursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
