""" Recent METARs containing some pattern """
import json

from pymemcache.client import Client
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconn, html_escape

json.encoder.FLOAT_REPR = lambda o: format(o, ".2f")


def trace(val):
    """Nice Print"""
    if val == TRACE_VALUE:
        return "T"
    return val


def get_data(q):
    """Get the data for this query"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    data = {"type": "FeatureCollection", "features": []}

    # Fetch the values
    countrysql = ""
    if q == "snowdepth":
        datasql = "substring(raw, ' 4/([0-9]{3})')::int"
        wheresql = "raw ~* ' 4/'"
    elif q == "i1":
        datasql = "ice_accretion_1hr"
        wheresql = "ice_accretion_1hr >= 0"
    elif q == "i3":
        datasql = "ice_accretion_3hr"
        wheresql = "ice_accretion_3hr >= 0"
    elif q == "i6":
        datasql = "ice_accretion_6hr"
        wheresql = "ice_accretion_6hr >= 0"
    elif q == "fc":
        datasql = "''"
        wheresql = "'FC' = ANY(wxcodes)"
    elif q == "gr":
        datasql = "''"
        wheresql = "'GR' = ANY(wxcodes)"
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
                    "valid": row["utc_valid"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [row["lon"], row["lat"]],
                },
            }
        )
    return json.dumps(data)


def application(environ, start_response):
    """see how we are called"""
    field = parse_formvars(environ)
    q = field.get("q", "snowdepth")[:10]
    cb = field.get("callback", None)

    headers = [("Content-type", "application/vnd.geo+json")]

    mckey = f"/geojson/recent_metar?callback={cb}&q={q}"
    mc = Client(["iem-memcached.local", 11211])
    res = mc.get(mckey)
    if not res:
        res = get_data(q)
        mc.set(mckey, res, 300)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]


if __name__ == "__main__":
    print(get_data("50A"))
