"""Generate a GeoJSON of current storm based warnings"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, title="JSONP Callback")


def run():
    """Actually do the hard work of getting the current SBW in geojson"""

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text("""
            SELECT ST_asGeoJson(ST_Transform(simple_geom, 4326)) as geojson,
            cond_code, c.segid from
            roads_current c JOIN roads_base b on (c.segid = b.segid)
            WHERE c.valid > now() - '1000 hours'::interval
            and cond_code is not null
        """)
        )

        data = {
            "type": "FeatureCollection",
            "features": [],
            "generated_at": utc().strftime(ISO8601),
            "count": res.rowcount,
        }
        for row in res:
            data["features"].append(
                dict(
                    type="Feature",
                    id=row[2],
                    properties=dict(code=row[1]),
                    geometry=json.loads(row[0]),
                )
            )

    return json.dumps(data)


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey="/geojson/winter_roads.geojson",
    memcacheexpire=120,
    content_type="application/vnd.geo+json",
)
def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]
    res = run()
    start_response("200 OK", headers)
    return res
