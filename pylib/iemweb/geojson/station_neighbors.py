""".. title:: GeoJSON of station neighbors

Return to `API Services </api/#json>`_

Documentation for /geojson/station_neighbors.py
-----------------------------------------------

For a given IEM tracked station, this service provides a GeoJSON representation
of the stations that are within a certain distance of the provided station.

Changelog
---------

- 2025-03-05: Initial implementation

Example Usage
-------------

Provide neighbors within 25 kilometers of the Ames Airport station.

https://mesonet.agron.iastate.edu/geojson/station_neighbors.py?\
station=AMW&network=IA_ASOS&distance=25

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp

from iemweb.util import get_ct


class Schema(CGIModel):
    """See how we are called."""

    callback: str | None = Field(
        default=None,
        description="JSONP callback function name",
        pattern=r"^[A-Za-z_$][0-9A-Za-z_$]*(?:\.[A-Za-z_$][0-9A-Za-z_$]*)*$",
        max_length=64,
    )
    network: str = Field(..., description="IEM Network Code", max_length=30)
    station: str = Field(
        ..., description="IEM Station Identifier", max_length=30
    )
    distance: float = Field(
        25.0,
        description="Distance in kilometers to search for neighbors",
        gt=0,
        le=1000,
    )
    only_online: bool = Field(
        False, description="Only include online stations"
    )
    fmt: str = Field(
        default="geojson",
        description="Output format (fixed to geojson).",
        pattern=r"^geojson$",
    )


def run(conn, environ: dict):
    """Generate a GeoJSON dump of the provided network"""
    cursor = conn.execute(
        sql_helper(
            "select st_x(geom), st_y(geom) from stations where id = :station "
            "and network = :network",
        ),
        environ,
    )
    if cursor.rowcount == 0:
        raise IncompleteWebRequest("Station not found")
    environ["lon"], environ["lat"] = cursor.fetchone()
    cursor = conn.execute(
        sql_helper("""
    with neighbors as (
        select ST_Distance(geom::geography, ST_Point(:lon, :lat, 4326))
        as dist, iemid from stations where id != :station
        and network != :network and ST_Distance(geom::geography,
        ST_Point(:lon, :lat, 4326)) < :distance * 1000.
    ), attrs as (
        SELECT t.iemid, t.dist, string_agg(a.attr, '____') as attrs,
        string_agg(a.value, '____') as attr_values
        from neighbors t LEFT JOIN station_attributes a
        on (t.iemid = a.iemid) GROUP by t.iemid, t.dist)
    SELECT t.*, a.dist, ST_AsGeoJSON(t.geom, 4) as geojson,
    coalesce(a.attrs, '') as attrs,
    coalesce(a.attr_values, '') as attr_values from stations t JOIN attrs a on
    (t.iemid = a.iemid) ORDER by dist ASC
        """),
        environ,
    )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utc().strftime(ISO8601),
        "count": cursor.rowcount,
    }

    for row in cursor.mappings():
        ab = row["archive_begin"]
        ae = row["archive_end"]
        time_domain = (
            f"({'????' if ab is None else ab.year}-"
            f"{'Now' if ae is None else ae.year})"
        )
        res["features"].append(
            dict(
                type="Feature",
                id=row["id"],
                properties=dict(
                    distance_km=int(row["dist"] / 1_000.0),
                    elevation=row["elevation"],
                    sname=row["name"],
                    time_domain=time_domain,
                    archive_begin=None if ab is None else f"{ab:%Y-%m-%d}",
                    archive_end=None if ae is None else f"{ae:%Y-%m-%d}",
                    state=row["state"],
                    country=row["country"],
                    climate_site=row["climate_site"],
                    wfo=row["wfo"],
                    tzname=row["tzname"],
                    ncdc81=row["ncdc81"],
                    ncei91=row["ncei91"],
                    ugc_county=row["ugc_county"],
                    ugc_zone=row["ugc_zone"],
                    county=row["county"],
                    sid=row["id"],
                    network=row["network"],
                    online=row["online"],
                    synop=row["synop"],
                    attributes=dict(
                        zip(
                            row["attrs"].split("____"),
                            row["attr_values"].split("____"),
                            strict=False,
                        )
                    ),
                ),
                geometry=json.loads(row["geojson"]),
            )
        )
    return json.dumps(res, ensure_ascii=False)


def get_mckey(environ) -> str:
    """Get the memcache key"""
    return (
        f"/geojson/sn/{environ['station']}/{environ['distance']}"
        f"{environ['network']}/{environ['only_online']}"
    )


@iemapp(
    memcachekey=get_mckey,
    memcacheexpire=86400,
    content_type=get_ct,
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", get_ct(environ))]
    with get_sqlalchemy_conn("mesosite") as conn:
        res = run(conn, environ)
    cb = environ.get("callback")
    payload = f"{cb}({res});" if cb else res
    start_response("200 OK", headers)
    return payload.encode("utf-8")
