""".. title:: Storm Prediction Center Mesoscale Convective Discussion

Documentation for /cgi-bin/request/gis/spc_mcd.py
-------------------------------------------------

The IEM archives Storm Prediction Center Mesoscale Convective Discussions (MCD)
in real-time and makes them available for download via this service.  The
raw product text is not emitted here, but the ``prod_id`` is included, which
is a reference to the raw product text.

Changelog
---------

- 2025-03-12: Added new Most Probable Intensity tags
- 2024-05-29: Initial documentation

Example Usage
-------------

Return all MCDs for 2023

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/spc_mcd.py?\
sts=2023-01-01T00:00Z&ets=2024-01-01T00:00Z

"""

import tempfile
import zipfile
from collections.abc import Callable
from io import BytesIO
from typing import Annotated

import geopandas as gpd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD,
    MINUTE_FIELD,
    MONTH_FIELD_OPTIONAL,
    YEAR_FIELD_OPTIONAL,
)
from pyiem.webutil import CGIModel, iemapp

PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


class Schema(CGIModel):
    """See how we are called."""

    sts: Annotated[AwareDatetime | None, Field(description="Start Time")] = (
        None
    )
    ets: Annotated[AwareDatetime | None, Field(description="End Time")] = None
    year1: YEAR_FIELD_OPTIONAL = None
    year2: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD = 0
    hour2: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    minute2: MINUTE_FIELD = 0


def run(query: Schema, start_response: Callable):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "ISSUE": "str:12",
            "EXPIRE": "str:12",
            "PROD_ID": "str:35",
            "YEAR": "int",
            "NUM": "int",
            "CONFIDEN": "int",
            "CONCERN": "str:64",
            "MP_TORN": "str:32",
            "MP_HAIL": "str:32",
            "MP_GUST": "str:32",
        },
    }
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(  # type: ignore
            sql_helper(
                """select to_char(issue {common}) as issue,
            to_char(expire {common}) as expire,
            product_id as prod_id, year, num, watch_confidence as confiden,
            concerning as concern, most_prob_tornado as mp_torn,
            most_prob_hail as mp_hail, most_prob_gust as mp_gust, geom
            from mcd WHERE issue >= :sts and
            issue < :ets ORDER by issue ASC""",
                common=common,
            ),
            conn,
            params={
                "sts": query.sts,
                "ets": query.ets,
            },
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return "ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"mcd_{query.sts:%Y%m%d%H%M}_{query.ets:%Y%m%d%H%M}"

    with tempfile.TemporaryDirectory() as tmpdir:
        df.to_file(f"{tmpdir}/{fn}.shp", schema=schema, engine="fiona")

        zio = BytesIO()
        with zipfile.ZipFile(
            zio, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            with open(PRJFILE, encoding="utf-8") as fh:
                zf.writestr(f"{fn}.prj", fh.read())
            for suffix in ["shp", "shx", "dbf"]:
                zf.write(f"{tmpdir}/{fn}.{suffix}", f"{fn}.{suffix}")
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.zip"),
    ]
    start_response("200 OK", headers)

    return zio.getvalue()


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ: dict, start_response: Callable):
    """Do something fun!"""
    query: Schema = environ["_cgimodel_schema"]
    if query.sts is None or query.ets is None:
        raise IncompleteWebRequest("GET sts/ets parameter not provided")
    if query.sts > query.ets:
        query.sts, query.ets = query.ets, query.sts
    return run(query, start_response)
