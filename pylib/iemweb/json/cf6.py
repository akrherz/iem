""".. title:: NWS CF6 JSON Service

Return to `JSON Services</json/>`_

Documentation for /json/cf6.py
------------------------------

This service emits atomic parsed data from the NWS CF6 product.

"""

import datetime

import simplejson as json
from pydantic import Field
from pyiem.reference import TRACE_VALUE
from pyiem.webutil import CGIModel, iemapp
from simplejson import encoder

encoder.FLOAT_REPR = lambda o: format(o, ".2f")


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    fmt: str = Field(
        default="json",
        description="The format of the output, either csv or json",
        pattern="^(json|csv)$",
    )
    station: str = Field(
        "KDSM", description="The station identifier", max_length=4
    )
    year: int = Field(2019, description="The year of interest")


def departure(ob, climo):
    """Compute a departure value"""
    if ob is None or climo is None:
        return "M"
    return ob - climo


def int_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return int(val)


def f1_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return round(val, 1)


def f2_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return round(val, 2)


def get_data(cursor, station, year, fmt):
    """Get the data for this timestamp"""
    data = {"results": []}
    # Fetch the daily values
    cursor.execute(
        """
        select station, name, product, state, wfo, valid,
        round(st_x(geom)::numeric, 4)::float as st_x,
        round(st_y(geom)::numeric, 4)::float as st_y,
        high, low, avg_temp, dep_temp, hdd, cdd, precip, snow, snowd_12z,
        avg_smph, max_smph, avg_drct, minutes_sunshine, possible_sunshine,
        cloud_ss, wxcodes, gust_smph, gust_drct
        from cf6_data c JOIN stations s on (c.station = s.id)
        WHERE s.network = 'NWSCLI' and c.station = %s
        and c.valid >= %s and c.valid <= %s
        ORDER by c.valid ASC
    """,
        (station, datetime.date(year, 1, 1), datetime.date(year, 12, 31)),
    )
    for row in cursor:
        data["results"].append(
            {
                "station": row["station"],
                "valid": row["valid"].strftime("%Y-%m-%d"),
                "state": row["state"],
                "wfo": row["wfo"],
                "link": f"/api/1/nwstext/{row['product']}",
                "product": row["product"],
                "name": row["name"],
                "high": int_sanitize(row["high"]),
                "low": int_sanitize(row["low"]),
                "avg_temp": f1_sanitize(row["avg_temp"]),
                "dep_temp": f1_sanitize(row["dep_temp"]),
                "hdd": int_sanitize(row["hdd"]),
                "cdd": int_sanitize(row["cdd"]),
                "precip": f2_sanitize(row["precip"]),
                "snow": f1_sanitize(row["snow"]),
                "snowd_12z": f1_sanitize(row["snowd_12z"]),
                "avg_smph": f1_sanitize(row["avg_smph"]),
                "max_smph": f1_sanitize(row["max_smph"]),
                "avg_drct": int_sanitize(row["avg_drct"]),
                "minutes_sunshine": int_sanitize(row["minutes_sunshine"]),
                "possible_sunshine": int_sanitize(row["possible_sunshine"]),
                "cloud_ss": f1_sanitize(row["cloud_ss"]),
                "wxcodes": row["wxcodes"],
                "gust_smph": f1_sanitize(row["gust_smph"]),
                "gust_drct": int_sanitize(row["gust_drct"]),
            }
        )
    if fmt == "json":
        return json.dumps(data)
    cols = (
        "station,valid,name,state,wfo,high,low,avg_temp,dep_temp,hdd,cdd,"
        "precip,snow,snowd_12z,avg_smph,max_smph,avg_drct,minutes_sunshine,"
        "possible_sunshine,cloud_ss,wxcodes,gust_smph,gust_drct"
    )
    res = cols + "\n"
    for feat in data["results"]:
        for col in cols.split(","):
            val = feat[col]
            if isinstance(val, (list, tuple)):
                res += f"{' '.join([str(s) for s in val])},"
            else:
                res += f"{val},"
        res += "\n"
    return res


def get_mckey(environ):
    """Generate the memcache key"""
    return f"/json/cf6/{environ['station']}/{environ['year']}/{environ['fmt']}"


def get_ct(environ):
    """Get the content type."""
    if environ["fmt"] == "json":
        return "application/json"
    return "text/plain"


@iemapp(
    iemdb="iem",
    iemdb_cursorname="cursor",
    help=__doc__,
    schema=Schema,
    memcachekey=get_mckey,
    content_type=get_ct,
)
def application(environ, start_response):
    """Answer request."""
    station = environ["station"]
    year = environ["year"]

    res = get_data(environ["iemdb.iem.cursor"], station, year, environ["fmt"])
    headers = [("Content-type", get_ct(environ))]
    start_response("200 OK", headers)
    return res
