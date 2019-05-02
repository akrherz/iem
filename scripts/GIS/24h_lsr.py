"""Dump 24 hour LSRs to a file"""
import zipfile
import os
from collections import OrderedDict
import shutil
import subprocess
import datetime

from geopandas import read_postgis
from pyiem.util import get_dbconn

SCHEMA = {
    'geometry': 'Point',
    'properties': OrderedDict([
        ('VALID', 'str:12'),
        ('MAG', 'float'),
        ('WFO', 'str:3'),
        ('TYPECODE', 'str:1'),
        ('TYPETEXT', 'str:40'),
        ('CITY', 'str:40'),
        ('COUNTY', 'str:40'),
        ('STATE', 'str:2'),
        ('SOURCE', 'str:40'),
        ('REMARK', 'str:200'),
        ('LON', 'float'),
        ('LAT', 'float')
    ])
}


def main():
    """Go Main Go"""
    pgconn = get_dbconn('postgis', user='nobody')

    os.chdir("/tmp/")

    # We set one minute into the future, so to get expiring warnings
    # out of the shapefile
    ets = datetime.datetime.utcnow() + datetime.timedelta(minutes=+1)

    df = read_postgis("""
        SELECT distinct geom,
        to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as VALID,
        coalesce(magnitude, 0)::float as MAG,
        wfo as WFO,
        type as TYPECODE,
        typetext as TYPETEXT,
        city as CITY,
        county as COUNTY,
        state as STATE,
        source as SOURCE,
        substr(remark, 1, 200) as REMARK,
        ST_x(geom) as LON,
        ST_y(geom) as LAT
        from lsrs_%s WHERE valid > (now() -'1 day'::interval)
    """ % (ets.year,), pgconn, index_col=None, geom_col='geom')
    df.columns = [s.upper() if s != 'geom' else 'geom' for s in df.columns]
    df.to_file("lsr_24hour.shp", schema=SCHEMA)
    df.to_file("lsr_24hour.geojson", driver='GeoJSON')
    df.to_csv("lsr_24hour.csv", index=False)

    zfh = zipfile.ZipFile("lsr_24hour.zip", 'w', zipfile.ZIP_DEFLATED)
    zfh.write("lsr_24hour.shp")
    zfh.write("lsr_24hour.shx")
    zfh.write("lsr_24hour.dbf")
    shutil.copy('/opt/iem/data/gis/meta/4326.prj', 'lsr_24hour.prj')
    zfh.write("lsr_24hour.prj")
    zfh.close()

    cmd = ("/home/ldm/bin/pqinsert -i "
           "-p \"zip c %s gis/shape/4326/us/lsr_24hour.zip "
           "bogus zip\" lsr_24hour.zip") % (ets.strftime("%Y%m%d%H%M"),)
    subprocess.call(cmd, shell=True)
    for suffix in ['geojson', 'csv']:
        cmd = (
            "/home/ldm/bin/pqinsert -i "
            "-p \"data c %s gis/shape/4326/us/lsr_24hour.%s "
            "bogus %s\" lsr_24hour.%s"
        ) % (ets.strftime("%Y%m%d%H%M"), suffix, suffix, suffix)
        subprocess.call(cmd, shell=True)

    for suffix in ['shp', 'shx', 'dbf', 'prj', 'zip', 'geojson', 'csv']:
        os.remove('lsr_24hour.%s' % (suffix,))


if __name__ == '__main__':
    main()
