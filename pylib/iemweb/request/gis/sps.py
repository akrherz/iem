""".. title:: Special Weather Statement (SPS) Data Service

Return to `API Services </api/#cgi>`_ or
`SPS Download Frontend </request/gis/sps.phtml>`_.

Documentation for /cgi-bin/request/gis/sps.py
---------------------------------------------

This service emits a shapefile of Special Weather Statements (SPS) data.

Changelog
---------

- 2024-09-23: Initial documentation release

Example Requests
----------------

Provide a zip file of SPS data from August 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/sps.py?\
sts=2024-08-01T00:00Z&ets=2024-09-01T00:00Z

"""

import tempfile
import zipfile
from io import BytesIO
from typing import Annotated

import geopandas as gpd
from pydantic import AwareDatetime, Field, model_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD,
    MINUTE_FIELD,
    MONTH_FIELD_OPTIONAL,
    VTEC_YEAR_FIELD_OPTIONAL,
)
from pyiem.webutil import CGIModel, iemapp

PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


class Schema(CGIModel):
    """See how we are called."""

    sts: Annotated[
        AwareDatetime | None,
        Field(description="Start timestamp for the data request"),
    ] = None
    ets: Annotated[
        AwareDatetime | None,
        Field(description="End timestamp for the data request"),
    ] = None
    year1: VTEC_YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    year2: VTEC_YEAR_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour2: HOUR_FIELD = 0
    minute2: MINUTE_FIELD = 0

    @model_validator(mode="after")
    def validate_times(self):
        """Ensure that start and end timestamps are available."""
        if self.sts is None or self.ets is None:
            raise ValueError("Both sts and ets need to be set.")
        return self


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "ISSUE": "str:12",
            "EXPIRE": "str:12",
            "PROD_ID": "str:36",
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
        df = gpd.read_postgis(  # type: ignore
            sql_helper(
                """
            select to_char(issue {common}) as issue,
            to_char(expire {common}) as expire, product_id as prod_id,
            wfo, landspout as lndspout, waterspout as wtrspout,
            max_hail_size as max_hail, max_wind_gust as max_wind,
            to_char(tml_valid {common}) as tml_vald,
            tml_direction as tml_drct,
            tml_sknt, geom from sps WHERE issue >= :sts and
            issue < :ets and not ST_isempty(geom) ORDER by issue ASC
            """,
                common=common,
            ),
            pgconn,
            params=ctx,
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"sps_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

    with tempfile.TemporaryDirectory() as tmpdir:
        df.to_file(f"{tmpdir}/{fn}.shp", schema=schema, engine="fiona")

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


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Do something fun!"""
    ctx = {"sts": environ["sts"], "ets": environ["ets"]}
    return run(ctx, start_response)
