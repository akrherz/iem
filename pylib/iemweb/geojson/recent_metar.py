""".. title:: Recent METAR GeoJSON

Return to `API Services </api/#json>`_

Service returns interesting METAR reports.

Changelog
---------

- 2026-05-14: Added pwino option.
- 2024-08-14: Documentation Update

Example Requests
----------------

Get the most recent snow depth reports

https://mesonet.agron.iastate.edu/geojson/recent_metar.py?q=snowdepth

Get the recent ice accretion 1 hour reports

https://mesonet.agron.iastate.edu/geojson/recent_metar.py?q=i1

Get the recent ice accretion 3 hour reports

https://mesonet.agron.iastate.edu/geojson/recent_metar.py?q=i3

Get the recent ice accretion 6 hour reports

https://mesonet.agron.iastate.edu/geojson/recent_metar.py?q=i6

Get any recent funnel cloud / tornado reports

https://mesonet.agron.iastate.edu/geojson/recent_metar.py?q=fc

Get any recent 50 knot wind reports

https://mesonet.agron.iastate.edu/geojson/recent_metar.py?q=50

Get any recent reports with `PNO` in the METAR

https://mesonet.agron.iastate.edu/geojson/recent_metar.py?q=pno

Return any recent METARs with the PWINO code included

https://mesonet.agron.iastate.edu/geojson/recent_metar.py?q=pwino
"""

import json
from typing import Annotated

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.reference import ISO8601, TRACE_VALUE
from pyiem.web.fields import CALLBACK_FIELD
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection

from iemweb.util import get_ct, json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
    q: Annotated[
        str,
        Field(
            description=(
                "The query to perform, one of snowdepth, "
                "i1, i3, i6, fc, gr, pno, 50, 50A, pwino"
            ),
            pattern="^(snowdepth|i1|i3|i6|fc|gr|pno|50|50A|pwino)$",
        ),
    ] = "snowdepth"
    fmt: Annotated[str, Field(description="Output format")] = "geojson"


def trace(val):
    """Nice Print"""
    if val == TRACE_VALUE:
        return "T"
    if isinstance(val, float):
        return round(val, 2)
    return val


def get_data(q, conn: Connection):
    """Get the data for this query"""
    data = json_response_dict({"type": "FeatureCollection", "features": []})

    # Fetch the values
    countrysql = ""
    if q == "snowdepth":
        datasql = "substring(raw, ' 4/([0-9]{3})')::int"
        wheresql = "raw ~* ' 4/'"
    elif q in ["i1", "i3", "i6"]:
        i = int(q[1])
        datasql = f"ice_accretion_{i}hr"
        wheresql = f"ice_accretion_{i}hr >= 0"
    elif q in ["fc", "gr"]:
        datasql = "''"
        wheresql = f"'{q.upper()}' = ANY(wxcodes)"
    elif q == "pno":
        datasql = "''"
        wheresql = "raw ~* ' PNO'"
    elif q in ["50", "50A"]:
        datasql = "greatest(sknt, gust)"
        wheresql = "(sknt >= 50 or gust >= 50)"
        if q == "50":
            countrysql = "and country = 'US'"
    elif q == "pwino":
        datasql = "''"
        wheresql = "raw ~* ' PWINO'"
    else:
        return json.dumps(data, ensure_ascii=False)
    res = conn.execute(
        sql_helper(
            """
    select id, network, name, st_x(geom) as lon, st_y(geom) as lat,
    valid at time zone 'UTC' as utc_valid, {datasql} as data, raw
    from current_log c JOIN stations t on (c.iemid = t.iemid)
    WHERE network ~* 'ASOS' {countrysql}
    and {wheresql} ORDER by valid DESC
    """,
            datasql=datasql,
            wheresql=wheresql,
            countrysql=countrysql,
        )
    )
    for i, row in enumerate(res.mappings()):
        data["features"].append(
            {
                "type": "Feature",
                "id": i,
                "properties": {
                    "station": row["id"],
                    "network": row["network"],
                    "name": row["name"],
                    "value": trace(row["data"]),
                    "metar": row["raw"],
                    "valid": row["utc_valid"].strftime(ISO8601),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [row["lon"], row["lat"]],
                },
            }
        )
    return json.dumps(data)


@iemapp(
    content_type=get_ct,
    memcachekey=lambda req: f"/geojson/recent_metar?q={req['q']}",
    memcacheexpire=120,
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """see how we are called"""
    headers = [("Content-type", get_ct(environ))]
    with get_sqlalchemy_conn("iem") as conn:
        res = get_data(environ["q"], conn)
    start_response("200 OK", headers)
    return res
