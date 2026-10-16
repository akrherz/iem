""".. title:: NWS Text GeoJSON (geo-encoded by issuance location)

Return to `API Services </api/#json>`_ or
`Climodat Frontend </COOP/extremes.php>`_.

Documentation for /geojson/nwstext.py
-------------------------------------

This service emits metadata for NWS Text Products geo-located by the issuance
center.  This is not an exact science and the points are simply the location
of the issuance center and not geometries provided within the text.  Feedback
is certainly welcome on the usefulness of this service.

Changelog
---------

- **2026-10-16**: Initial release.

Usage Examples
~~~~~~~~~~~~~~

Provide the nearest in time (looking either forward or backward,
within 12 hours) Area Forecast Discussion (AFD) approximately valid
at 12 UTC 12 July 2024.

https://mesonet.agron.iastate.edu/geojson/nwstext.py\
?hours=12&valid=2024-07-12T12:00:00Z&direction=around&pil=AFD

Same request, but only looking backward in time.

https://mesonet.agron.iastate.edu/geojson/nwstext.py\
?hours=12&valid=2024-07-12T12:00:00Z&direction=backward&pil=AFD

Same request, but forward in time.

https://mesonet.agron.iastate.edu/geojson/nwstext.py\
?hours=12&valid=2024-07-12T12:00:00Z&direction=forward&pil=AFD

"""

import json
from datetime import timedelta
from typing import Annotated

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.web.fields import CALLBACK_FIELD
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import Connection

from iemweb.mlib import unrectify_wfo
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
    hours: Annotated[int, Field(ge=1, le=72)] = 1
    valid: Annotated[
        AwareDatetime,
        Field(
            default_factory=lambda: utc().replace(second=0, minute=0),
            description=("Timestamp to retrieve products approximate for."),
        ),
    ]
    direction: Annotated[
        str,
        Field(
            description=(
                "Direction to look for the nearest product in time. "
                "Valid values are 'forward', 'backward' or 'around'. "
                "Around is default.  Boundaries are inclusive."
            ),
            pattern="^(forward|backward|around)$",
        ),
    ] = "around"
    pil: Annotated[
        str,
        Field(
            description=(
                "Product Identifier (PIL) to filter the NWS Text Products."
            ),
            pattern="^[A-Z0-9]{3}$",
        ),
    ] = "AFD"


def generate_res(conn: Connection, query: Schema):
    """Do something"""
    sts = query.valid - timedelta(hours=query.hours)
    ets = query.valid + timedelta(hours=query.hours)
    if query.direction == "forward":
        sts = query.valid
    elif query.direction == "backward":
        ets = query.valid

    nt = NetworkTable(["WFO", "NCEP", "RFC", "NWS", "CWSU"])
    res = conn.execute(
        sql_helper(
            """
        with data as (
        select entered at time zone 'UTC' as utc_entered,
        source, wmo, pil, bbb,
        row_number() OVER (
            PARTITION by source
            ORDER by abs(extract(epoch from (entered - :valid))) ASC, bbb ASC
        ) from products
        where substr(pil, 1, 3) = :pil and entered >= :sts and entered <= :ets
        )
        select * from data where row_number = 1
    """,
        ),
        {
            "pil": query.pil,
            "valid": query.valid,
            "sts": sts,
            "ets": ets,
        },
    )
    data = json_response_dict(
        {
            "type": "FeatureCollection",
            "pil": query.pil,
            "valid": query.valid.strftime(ISO8601),
            "direction": query.direction,
            "hours": query.hours,
            "features": [],
        }
    )

    for i, row in enumerate(res.mappings()):
        lookup_key = unrectify_wfo(row["source"])
        if lookup_key not in nt.sts:
            continue
        product_id = (
            f"{row['utc_entered']:%Y%m%d%H%M}-{row['source']}-{row['wmo']}-"
            f"{row['pil']}"
        )
        if row["bbb"]:
            product_id += f"-{row['bbb']}"
        props = {
            "url": f"/api/1/nwstext/{product_id}",
            "product_valid": row["utc_entered"].strftime(ISO8601),
            "source_name": nt.sts[lookup_key]["name"],
            "pil": row["pil"],
        }
        data["features"].append(
            {
                "type": "Feature",
                "id": i,
                "properties": props,
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        nt.sts[lookup_key]["lon"],
                        nt.sts[lookup_key]["lat"],
                    ],
                },
            }
        )

    return json.dumps(data)


def get_mckey(environ: dict) -> str:
    """Get the memcache key"""
    query: Schema = environ["_cgimodel_schema"]
    return (
        f"/geojson/nwstext/{query.direction}/"
        f"{query.valid:%Y%m%d%H%M}/{query.pil}/{query.hours}"
    )


@iemapp(
    help=__doc__,
    memcacheexpire=300,
    memcachekey=get_mckey,
    schema=Schema,
    content_type="application/vnd.geo+json",
)
def application(environ, start_response):
    """Main()"""
    headers = [("Content-type", "application/vnd.geo+json")]

    query: Schema = environ["_cgimodel_schema"]

    with get_sqlalchemy_conn("afos") as conn:
        res = generate_res(conn, query)

    start_response("200 OK", headers)
    return res.encode("utf-8", "ignore")
