"""create initial database entries"""
from __future__ import print_function
import os
import glob
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


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

    os.chdir("/mesonet/data/dotcams")
    files = glob.glob("*640x480.jpg")
    for fn in files:
        cid = fn[:11]

        cursor.execute(
            """
            SELECT * from webcams WHERE id = %s
        """,
            (cid,),
        )
        if cursor.rowcount > 0:
            continue

        rid = cid[6:8]
        nwsli = find_id(nt, int(rid))
        if nwsli is None:
            print("Failed to find remote_id: %s" % (rid,))
            continue

        cursor.execute(
            """
            SELECT name, ST_x(geom) as lon, ST_y(geom) as lat
            from stations where id = %s
        """,
            (nwsli,),
        )
        row = cursor.fetchone()
        lon = row[1]
        lat = row[2]
        name = row[0]
        print(
            ("Adding %s name [%s] lon [%s] lat [%s]") % (cid, name, lon, lat)
        )
        sql = """
            insert into webcams (sts, id, name, pan0, online, network,
            geom, removed, state) values (now(), '%s', '%s', 0, 't',
            'IDOT', 'SRID=4326;POINT(%s %s)', 'f', 'IA')
        """ % (
            cid,
            name,
            lon,
            lat,
        )
        cursor.execute(sql)
    cursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
