""".. title:: Recent METAR GeoJSON

Return to `API Services </api/#json>`_

Service returns interesting METAR reports.

Changelog
---------

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

"""

import json

from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601, TRACE_VALUE
from pyiem.webutil import CGIModel, iemapp

json.encoder.FLOAT_REPR = lambda o: format(o, ".2f")


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    q: str = Field(
        "snowdepth",
        description=(
            "The query to perform, one of snowdepth, "
            "i1, i3, i6, fc, gr, pno, 50, 50A"
        ),
        pattern="^(snowdepth|i1|i3|i6|fc|gr|pno|50|50A)$",
    )


def trace(val):
    """Nice Print"""
    if val == TRACE_VALUE:
        return "T"
    return val


def get_data(q):
    """Get the data for this query"""
    pgconn, cursor = get_dbconnc("iem")
    data = {"type": "FeatureCollection", "features": []}

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
    else:
        return json.dumps(data)
    cursor.execute(
        f"""
    select id, network, name, st_x(geom) as lon, st_y(geom) as lat,
    valid at time zone 'UTC' as utc_valid, {datasql} as data, raw
    from current_log c JOIN stations t on (c.iemid = t.iemid)
    WHERE network ~* 'ASOS' {countrysql}
    and {wheresql} ORDER by valid DESC
    """
    )
    for i, row in enumerate(cursor):
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
    pgconn.close()
    return json.dumps(data)


@iemapp(
    content_type="application/vnd.geo+json",
    memcachekey=lambda req: f"/geojson/recent_metar?{req['q']}",
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """see how we are called"""
    headers = [("Content-type", "application/vnd.geo+json")]
    res = get_data(environ["q"])
    start_response("200 OK", headers)
    return res.encode("ascii")
