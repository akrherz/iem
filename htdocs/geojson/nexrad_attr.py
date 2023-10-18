""" Generate a GeoJSON of nexrad attributes"""
import datetime
import json
from zoneinfo import ZoneInfo

from pyiem.util import get_dbconnc, html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client


def run(ts, fmt):
    """Actually do the hard work of getting the geojson"""
    pgconn, cursor = get_dbconnc("radar")

    utcnow = datetime.datetime.utcnow()

    if ts == "":
        cursor.execute(
            """
            SELECT ST_x(geom) as lon, ST_y(geom) as lat, *,
            valid at time zone 'UTC' as utc_valid from
            nexrad_attributes WHERE valid > now() - '30 minutes'::interval
        """
        )
    else:
        try:
            valid = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return "ERROR"
        valid = valid.replace(tzinfo=ZoneInfo("UTC"))
        tbl = "nexrad_attributes_%s" % (valid.year,)
        cursor.execute(
            f"""
        with vcps as (
            SELECT distinct nexrad, valid from {tbl}
            where valid between %s and %s),
        agg as (
            select nexrad, valid,
            row_number() OVER (PARTITION by nexrad
                ORDER by (greatest(valid, %s) - least(valid, %s)) ASC)
            as rank from vcps)
        SELECT n.*, ST_x(geom) as lon, ST_y(geom) as lat,
        n.valid at time zone 'UTC' as utc_valid
        from {tbl} n, agg a WHERE
        a.rank = 1 and a.nexrad = n.nexrad and a.valid = n.valid
        ORDER by n.nexrad ASC
        """,
            (
                valid - datetime.timedelta(minutes=10),
                valid + datetime.timedelta(minutes=10),
                valid,
                valid,
            ),
        )

    if fmt == "geojson":
        res = {
            "type": "FeatureCollection",
            "features": [],
            "generation_time": utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "count": cursor.rowcount,
        }
        for i, row in enumerate(cursor):
            res["features"].append(
                {
                    "type": "Feature",
                    "id": i,
                    "properties": {
                        "nexrad": row["nexrad"],
                        "storm_id": row["storm_id"],
                        "azimuth": row["azimuth"],
                        "range": row["range"],
                        "tvs": row["tvs"],
                        "meso": row["meso"],
                        "posh": row["posh"],
                        "poh": row["poh"],
                        "max_size": row["max_size"],
                        "vil": row["vil"],
                        "max_dbz": row["max_dbz"],
                        "max_dbz_height": row["max_dbz_height"],
                        "top": row["top"],
                        "drct": row["drct"],
                        "sknt": row["sknt"],
                        "valid": row["utc_valid"].strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row["lon"], row["lat"]],
                    },
                }
            )
        pgconn.close()
        return json.dumps(res)
    res = (
        "nexrad,storm_id,azimuth,range,tvs,meso,posh,poh,max_size,"
        "vil,max_dbz,max_dbz_height,top,drct,sknt,valid\n"
    )
    for row in cursor:
        res += ",".join(
            [
                str(x)
                for x in [
                    row["nexrad"],
                    row["storm_id"],
                    row["azimuth"],
                    row["range"],
                    row["tvs"],
                    row["meso"],
                    row["posh"],
                    row["poh"],
                    row["max_size"],
                    row["vil"],
                    row["max_dbz"],
                    row["max_dbz_height"],
                    row["top"],
                    row["drct"],
                    row["sknt"],
                    row["utc_valid"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                ]
            ]
        )
        res += "\n"
    pgconn.close()
    return res


@iemapp()
def application(environ, start_response):
    """Do Something"""
    # Go Main Go
    cb = environ.get("callback", None)
    ts = environ.get("valid", "")[:19]  # ISO-8601ish
    fmt = environ.get("fmt", "geojson")[:7]
    if fmt == "geojson":
        headers = [("Content-type", "application/vnd.geo+json")]
    else:
        headers = [("Content-type", "text/csv")]

    mckey = f"/geojson/nexrad_attr.{fmt}|{ts}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run(ts, fmt)
        mc.set(mckey, res, 30 if ts == "" else 3600)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None and fmt != "csv":
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]
