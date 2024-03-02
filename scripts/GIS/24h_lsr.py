"""Dump 24 hour LSRs to a file.

Called from RUN_5MIN.sh
"""

import datetime
import os
import subprocess
import tempfile
import zipfile

import geopandas as gpd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import logger, utc

LOG = logger()
FIELDS = {
    "VALID": "str:12",
    "MAG": "float",
    "WFO": "str:3",
    "TYPECODE": "str:1",
    "TYPETEXT": "str:40",
    "CITY": "str:40",
    "COUNTY": "str:40",
    "STATE": "str:2",
    "SOURCE": "str:40",
    "REMARK": "str:200",
    "LON": "float",
    "LAT": "float",
    "UGC": "str:6",
    "UGCNAME": "str:128",
}
SCHEMA = {"geometry": "Point", "properties": FIELDS}


def main():
    """Go Main Go"""
    # We set one minute into the future, so to get expiring warnings
    # out of the shapefile
    ets = utc() + datetime.timedelta(minutes=+1)
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            """
            SELECT distinct l.geom,
            to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as VALID,
            coalesce(magnitude, 0)::float as MAG,
            l.wfo as WFO,
            type as TYPECODE,
            typetext as TYPETEXT,
            city as CITY,
            county as COUNTY,
            l.state as STATE,
            l.source as SOURCE,
            substr(coalesce(remark, ''), 1, 200) as REMARK,
            ST_x(l.geom) as LON,
            ST_y(l.geom) as LAT,
            u.ugc as UGC,
            u.name as UGCNAME
            from lsrs l LEFT JOIN ugcs u on (l.gid = u.gid)
            WHERE valid > (now() -'1 day'::interval)
        """,
            conn,
            index_col=None,
            geom_col="geom",
        )
        LOG.info("Got %s rows", len(df.index))
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
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="ascii") as fh:
            zfh.writestr("lsr_24hour.prj", fh.read())
        zfh.getinfo("lsr_24hour.prj").external_attr = 0o664

    pstr = f"zip c {ets:%Y%m%d%H%M} gis/shape/4326/us/lsr_24hour.zip bogus zip"
    LOG.info(pstr)
    subprocess.call(["pqinsert", "-i", "-p", pstr, "lsr_24hour.zip"])
    for suffix in ["geojson", "csv"]:
        pstr = (
            f"data c {ets:%Y%m%d%H%M} "
            f"gis/shape/4326/us/lsr_24hour.{suffix} bogus {suffix}"
        )
        LOG.info(pstr)
        subprocess.call(["pqinsert", "-i", "-p", pstr, f"lsr_24hour.{suffix}"])


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as _tmpdir:
        os.chdir(_tmpdir)
        main()
