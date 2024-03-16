""".. title:: Special Weather Statement (SPS) Data Service

Documentation for /cgi-bin/request/gis/sps.py
---------------------------------------------

To be written.

"""

# Local
import tempfile
import zipfile
from io import BytesIO

# Third Party
import geopandas as gpd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import iemapp

PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "ISSUE": "str:12",
            "EXPIRE": "str:12",
            "PROD_ID": "str:32",
            "WFO": "str:3",
            "LNDSPOUT": "str:64",
            "WTRSPOUT": "str:64",
            "MAX_HAIL": "str:16",
            "MAX_WIND": "str:16",
            "TML_VALD": "str:12",
            "TML_DRCT": "int",
            "TML_SKNT": "int",
        },
    }
    with get_sqlalchemy_conn("postgis") as pgconn:
        df = gpd.read_postgis(
            "select "
            f"to_char(issue {common}) as issue, "
            f"to_char(expire {common}) as expire, "
            f"product_id as prod_id, "
            "wfo, landspout as lndspout, waterspout as wtrspout, "
            "max_hail_size as max_hail, max_wind_gust as max_wind, "
            f"to_char(tml_valid {common}) as tml_vald, "
            "tml_direction as tml_drct, "
            "tml_sknt, geom from sps WHERE issue >= %s and "
            "issue < %s and not ST_isempty(geom) ORDER by issue ASC",
            pgconn,
            params=(ctx["sts"], ctx["ets"]),
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"sps_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

    with tempfile.TemporaryDirectory() as tmpdir:
        df.to_file(f"{tmpdir}/{fn}.shp", schema=schema)

        zio = BytesIO()
        with zipfile.ZipFile(
            zio, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            with open(PRJFILE, encoding="ascii") as fp:
                zf.writestr(f"{fn}.prj", fp.read())
            for suffix in ("shp", "shx", "dbf"):
                zf.write(f"{tmpdir}/{fn}.{suffix}", f"{fn}.{suffix}")
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.zip"),
    ]
    start_response("200 OK", headers)

    return zio.getvalue()


@iemapp(default_tz="UTC", help=__doc__)
def application(environ, start_response):
    """Do something fun!"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start timestamp params missing")
    ctx = {"sts": environ["sts"], "ets": environ["ets"]}
    return [run(ctx, start_response)]
