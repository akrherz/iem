"""Dump 24 hour LSRs to a file"""
import zipfile
import os
import shutil
import subprocess
import datetime

from geopandas import read_postgis
from pyiem.util import get_sqlalchemy_conn

SCHEMA = {
    "geometry": "Point",
    "properties": dict(
        [
            ("VALID", "str:12"),
            ("MAG", "float"),
            ("WFO", "str:3"),
            ("TYPECODE", "str:1"),
            ("TYPETEXT", "str:40"),
            ("CITY", "str:40"),
            ("COUNTY", "str:40"),
            ("STATE", "str:2"),
            ("SOURCE", "str:40"),
            ("REMARK", "str:200"),
            ("LON", "float"),
            ("LAT", "float"),
        ]
    ),
}


def main():
    """Go Main Go"""
    os.chdir("/tmp/")

    # We set one minute into the future, so to get expiring warnings
    # out of the shapefile
    ets = datetime.datetime.utcnow() + datetime.timedelta(minutes=+1)
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_postgis(
            """
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
            substr(coalesce(remark, ''), 1, 200) as REMARK,
            ST_x(geom) as LON,
            ST_y(geom) as LAT
            from lsrs WHERE valid > (now() -'1 day'::interval)
        """,
            conn,
            index_col=None,
            geom_col="geom",
        )
    if df.empty:
        return
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    df.to_file("lsr_24hour.shp", schema=SCHEMA)
    df.to_file("lsr_24hour.geojson", driver="GeoJSON")
    df.to_csv("lsr_24hour.csv", index=False)

    with zipfile.ZipFile("lsr_24hour.zip", "w", zipfile.ZIP_DEFLATED) as zfh:
        zfh.write("lsr_24hour.shp")
        zfh.write("lsr_24hour.shx")
        zfh.write("lsr_24hour.dbf")
        shutil.copy("/opt/iem/data/gis/meta/4326.prj", "lsr_24hour.prj")
        zfh.write("lsr_24hour.prj")

    cmd = (
        "pqinsert -i "
        f'-p "zip c {ets:%Y%m%d%H%M} gis/shape/4326/us/lsr_24hour.zip '
        'bogus zip" lsr_24hour.zip'
    )
    subprocess.call(cmd, shell=True)
    for suffix in ["geojson", "csv"]:
        cmd = (
            "pqinsert -i "
            f'-p "data c {ets:%Y%m%d%H%M} '
            f"gis/shape/4326/us/lsr_24hour.{suffix} "
            f'bogus {suffix}" lsr_24hour.{suffix}'
        )
        subprocess.call(cmd, shell=True)

    for suffix in ["shp", "shx", "dbf", "prj", "zip", "geojson", "csv"]:
        os.remove(f"lsr_24hour.{suffix}")


if __name__ == "__main__":
    main()
