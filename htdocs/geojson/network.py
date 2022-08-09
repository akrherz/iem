"""GeoJSON of a given IEM network code"""
import json
import datetime

import psycopg2.extras
from pymemcache.client import Client
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape


def run(network, only_online):
    """Generate a GeoJSON dump of the provided network"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # One off special
    if network == "ASOS1MIN":
        cursor.execute(
            "SELECT ST_asGeoJson(geom, 4) as geojson, t.* "
            "from stations t JOIN station_attributes a "
            "ON (t.iemid = a.iemid) WHERE t.network ~* 'ASOS' and "
            "a.attr = 'HAS1MIN' ORDER by id ASC",
        )
    elif network == "FPS":
        cursor.execute(
            "SELECT ST_asGeoJson(geom, 4) as geojson, * "
            "from stations WHERE (network ~* 'ASOS' or network ~* 'CLIMATE') "
            "and country = 'US' and online ORDER by id ASC",
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
        "generation_time": datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
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
                ),
                geometry=json.loads(row["geojson"]),
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]

    form = parse_formvars(environ)
    cb = form.get("callback", None)
    network = form.get("network", "KCCI")
    only_online = form.get("only_online", "0") == "1"

    mckey = f"/geojson/network/{network}.geojson|{only_online}"
    mc = Client(["iem-memcached", 11211])
    res = mc.get(mckey)
    if not res:
        res = run(network, only_online)
        mc.set(mckey, res, 86400 if network == "FPS" else 3600)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]
