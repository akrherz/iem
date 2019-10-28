#!/usr/bin/env python
"""
Get storm based warnings by lat lon point
"""
import json

from paste.request import parse_formvars
from pyiem.util import get_dbconn


def get_events(lon, lat):
    """ Get Events """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute("""SET TIME ZONE 'UTC'""")
    cursor.execute(
        """
  select wfo, significance, phenomena, issue, expire, eventid from sbw
  where status = 'NEW' and
  ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT('POINT(%s %s)'),4326))
  and phenomena in ('SV', 'TO', 'FF', 'FL', 'MA', 'FA') and
  issue > '2005-10-01'
  ORDER by issue ASC
    """,
        (lon, lat),
    )
    data = {"sbws": []}
    for row in cursor:
        data["sbws"].append(
            {
                "phenomena": row[2],
                "eventid": row[5],
                "significance": row[1],
                "wfo": row[0],
                "issue": row[3].strftime("%Y-%m-%dT%H:%MZ"),
                "expire": row[4].strftime("%Y-%m-%dT%H:%MZ"),
            }
        )
    return data


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    lat = float(fields.get("lat", 41.99))
    lon = float(fields.get("lon", -92.0))

    data = get_events(lon, lat)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [json.dumps(data).encode("ascii")]
