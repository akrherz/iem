"""GeoJSON of a given IEM network code"""

import datetime
import json

from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    network: str = Field(
        "IA_ASOS", description="IEM Network Code", max_length=30
    )
    only_online: bool = Field(
        False, description="Only include online stations"
    )


def run(network, only_online):
    """Generate a GeoJSON dump of the provided network"""
    pgconn, cursor = get_dbconnc("mesosite")

    # One off special
    if network in ["ASOS1MIN", "TAF"]:
        cursor.execute(
            "SELECT ST_asGeoJson(geom, 4) as geojson, t.* "
            "from stations t JOIN station_attributes a "
            "ON (t.iemid = a.iemid) WHERE t.network ~* 'ASOS' and "
            "a.attr = %s ORDER by id ASC",
            ("HAS1MIN" if network == "ASOS1MIN" else "HASTAF",),
        )
    elif network == "FPS":
        cursor.execute(
            "SELECT ST_asGeoJson(geom, 4) as geojson, * "
            "from stations WHERE (network ~* 'ASOS' or ("
            "network ~* 'CLIMATE'and archive_begin < '1990-01-01') or "
            "network = 'ISUSM') "
            "and country = 'US' and online ORDER by id ASC",
        )
    elif network == "AZOS":
        cursor.execute(
            "SELECT ST_asGeoJson(geom, 4) as geojson, * "
            "from stations WHERE network ~* 'ASOS' and online ORDER by id ASC",
        )
    else:
        online = "and online" if only_online else ""
        cursor.execute(
            "SELECT ST_asGeoJson(geom, 4) as geojson, * from stations "
            f"WHERE network = %s {online} ORDER by name ASC",
            (network,),
        )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": datetime.datetime.utcnow().strftime(ISO8601),
        "count": cursor.rowcount,
    }
    for row in cursor:
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
                ),
                geometry=json.loads(row["geojson"]),
            )
        )
    pgconn.close()
    return json.dumps(res)


def get_mckey(environ) -> str:
    """Get the memcache key"""
    return (
        "/geojson/network/"
        f"{environ['network']}.geojson|{environ['only_online']}"
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

    res = run(network, only_online)
    start_response("200 OK", headers)
    return res
