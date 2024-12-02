""".. title:: GeoJSON of stations within a network

Return to `API Services </api/#json>`_

Documentation for /geojson/network.py
-------------------------------------

This service provides a GeoJSON representation of stations within a given
network.

Changelog
---------

- 2024-11-25: Added `network` overload value of `HAS_HML` for sites with HML
  data.
- 2024-08-19: Initial documentation update

Example Usage
-------------

Provide all sites with 1 minute ASOS data:

https://mesonet.agron.iastate.edu/geojson/network.py?network=ASOS1MIN

Provide all sites with TAF data:

https://mesonet.agron.iastate.edu/geojson/network.py?network=TAF

Provide sites that are online within ASOS class networks

https://mesonet.agron.iastate.edu/geojson/network.py?network=AZOS&only_online=1

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

XREF = {
    "HAS_HML": "HAS_HML",
    "ASOS1MIN": "HAS1MIN",
    "TAF": "HASTAF",
}


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    network: str = Field(
        "IA_ASOS", description="IEM Network Code", max_length=30
    )
    only_online: bool = Field(
        False, description="Only include online stations"
    )


def run(conn, network, only_online):
    """Generate a GeoJSON dump of the provided network"""
    params = {
        "network": network,
    }

    # One off special
    if network in XREF:
        subselect = "a.attr = :network"
        params["network"] = XREF[network]
    elif network == "FPS":
        subselect = """(network ~* 'ASOS' or (
            network ~* 'CLIMATE'and archive_begin < '1990-01-01') or
            network = 'ISUSM')
        and country = 'US' and online"""
    elif network == "AZOS":
        subselect = "network ~* 'ASOS' and online"
    else:
        subselect = "network = :network "
        subselect += "and online" if only_online else ""
    cursor = conn.execute(
        text(f"""
    WITH attrs as (
        SELECT t.iemid, string_agg(a.attr, '____') as attrs,
        string_agg(a.value, '____') as attr_values
        from stations t LEFT JOIN station_attributes a
        on (t.iemid = a.iemid) WHERE {subselect}
        GROUP by t.iemid)
    SELECT t.*, ST_AsGeoJSON(t.geom, 4) as geojson,
    coalesce(a.attrs, '') as attrs,
    coalesce(a.attr_values, '') as attr_values from stations t JOIN attrs a on
    (t.iemid = a.iemid) ORDER by t.id ASC
            """),
        params,
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
                        )
                    ),
                ),
                geometry=json.loads(row["geojson"]),
            )
        )
    return json.dumps(res)


def get_mckey(environ) -> str:
    """Get the memcache key"""
    return (
        "/geojson/network/"
        f"{environ['network']}.geojson|{environ['only_online']}/v2"
    )


@iemapp(
    memcachekey=get_mckey,
    memcacheexpire=86400,
    content_type="application/vnd.geo+json",
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]

    network = environ["network"]
    only_online = environ["only_online"]

    with get_sqlalchemy_conn("mesosite") as conn:
        res = run(conn, network, only_online)
    start_response("200 OK", headers)
    return res
