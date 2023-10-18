"""Generate a Watch Outline for a given SPC convective watch """
import zipfile
from io import BytesIO

import shapefile
from pyiem import wellknowntext
from pyiem.util import get_dbconnc
from pyiem.webutil import iemapp


def main(year, etn, start_response):
    """Go Main Go"""
    pgconn, cursor = get_dbconnc("postgis")

    basefn = f"watch_{year}_{etn}"

    cursor.execute(
        f"""select
        ST_astext(ST_multi(ST_union(ST_SnapToGrid(u.geom,0.0001)))) as tgeom
        from warnings_{year} w JOIN ugcs u on (u.gid = w.gid)
        WHERE significance = 'A'
        and phenomena IN ('TO','SV') and eventid = %s and
        ST_isvalid(u.geom)
        and issue < ((select issued from watches WHERE num = %s and
        extract(year from issued) = %s LIMIT 1) + '60 minutes'::interval)
        """,
        (etn, etn, year),
    )
    if cursor.rowcount == 0:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"No Data Found"
    row = cursor.fetchone()
    s = row["tgeom"]
    if s is None:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"No Data Found"

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()
    with shapefile.Writer(shx=shxio, shp=shpio, dbf=dbfio) as shp:
        shp.field("SIG", "C", "1")
        shp.field("ETN", "I", "4")

        f = wellknowntext.convert_well_known_text(s)
        shp.poly(f)
        shp.record("A", etn)

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="ascii") as fh:
            zf.writestr(f"{basefn}.prj", fh.read())
        zf.writestr(basefn + ".shp", shpio.getvalue())
        zf.writestr(basefn + ".shx", shxio.getvalue())
        zf.writestr(basefn + ".dbf", dbfio.getvalue())

    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={basefn}.zip"),
    ]
    pgconn.close()
    start_response("200 OK", headers)
    return zio.getvalue()


@iemapp()
def application(environ, start_response):
    """Yawn"""
    year = int(environ.get("year", 2018))
    etn = int(environ.get("etn", 1))

    return [main(year, etn, start_response)]
