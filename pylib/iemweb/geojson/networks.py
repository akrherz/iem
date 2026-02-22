""".. title:: IEM Networks GeoJSON

Return to `API Services </api/#json>`_

This service provides a GeoJSON representation of the IEM Networks.

Changelog
---------

- 2024-08-20: Initial documentation update

Example Usage
~~~~~~~~~~~~~

Request the GeoJSON representation of the IEM Networks:

https://mesonet.agron.iastate.edu/geojson/networks.py

"""

import json
from typing import Annotated

from pydantic import Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class Schema(CGIModel):
    """See how we are called."""

    callback: Annotated[
        str | None, Field(description="JSONP callback function")
    ] = None


@with_sqlalchemy_conn("mesosite")
def run(conn: Connection = None):
    """Actually do the hard work of getting the current SBW in geojson"""
    res = conn.execute(
        sql_helper(
            "SELECT ST_asGeoJson(extent) as geojson, id, name "
            "from networks WHERE extent is not null ORDER by id ASC"
        )
    )

    data = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utc().strftime(ISO8601),
        "count": res.rowcount,
    }
    for row in res.mappings():
        data["features"].append(
            dict(
                type="Feature",
                id=row["id"],
                properties=dict(name=row["name"]),
                geometry=json.loads(row["geojson"]),
            )
        )
    return json.dumps(data)


@iemapp(
    memcacheexpire=86400,
    memcachekey="/geojson/network.geojson",
    content_type="application/vnd.geo+json",
    help=__doc__,
    schema=Schema,
)
def application(_environ, start_response):
    """Do Something"""
    # Go Main Go
    headers = [("Content-type", "application/vnd.geo+json")]

    res = run()
    start_response("200 OK", headers)
    return res.encode("ascii")
