"""
Get storm based warnings by lat lon point, optionally a time
"""
import sys
import json
import datetime

from paste.request import parse_formvars
from pyiem.util import get_dbconn, utc

ISO = "%Y-%m-%dT%H:%M:%SZ"


def get_events(ctx):
    """ Get Events """
    data = {"sbws": [], "lon": ctx["lon"], "lat": ctx["lat"], "valid": None}
    data["generation_time"] = utc().strftime(ISO)
    valid_limiter = ""
    if "valid" in ctx:
        valid_limiter = " and issue <= '%s+00' and expire > '%s' " % (
            ctx["valid"].strftime("%Y-%m-%d %H:%M"),
            ctx["valid"].strftime("%Y-%m-%d %H:%M"),
        )
        data["valid"] = ctx["valid"].strftime(ISO)

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute("""SET TIME ZONE 'UTC'""")
    cursor.execute(
        """
  select wfo, significance, phenomena, issue, expire, eventid,
  tml_direction, tml_sknt, hvtec_nwsli from sbw
  where status = 'NEW' and
  ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT('POINT(%s %s)'),4326)) and
  issue > '2005-10-01' """
        + valid_limiter
        + """
  ORDER by issue ASC
    """,
        (ctx["lon"], ctx["lat"]),
    )
    for row in cursor:
        data["sbws"].append(
            {
                "phenomena": row[2],
                "eventid": row[5],
                "significance": row[1],
                "wfo": row[0],
                "issue": row[3].strftime("%Y-%m-%dT%H:%MZ"),
                "expire": row[4].strftime("%Y-%m-%dT%H:%MZ"),
                "tml_direction": row[6],
                "tml_sknt": row[7],
                "hvtec_nwsli": row[8],
            }
        )
    return data


def try_valid(ctx, fields):
    """See if a valid stamp is provided or not."""
    if fields.get("valid") is None:
        return
    # parse at least the YYYY-mm-ddTHH:MM
    ts = datetime.datetime.strptime(fields["valid"][:16], "%Y-%m-%dT%H:%M")
    ctx["valid"] = utc(ts.year, ts.month, ts.day, ts.hour, ts.minute)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    ctx = {}
    ctx["lat"] = float(fields.get("lat", 41.99))
    ctx["lon"] = float(fields.get("lon", -92.0))
    try:
        try_valid(ctx, fields)
    except Exception as exp:
        sys.stderr.write(str(exp))
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        return [b"Failed to parse valid, ensure YYYY-mm-ddTHH:MM:SSZ"]

    data = get_events(ctx)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [json.dumps(data).encode("ascii")]
