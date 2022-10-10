"""
Return JSON metadata for nexrad information
"""
import json
import datetime
import os.path
import glob

from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape

NIDS = {
    "N0B": "Base Reflectivity (Super Res)",
    "N0Q": "Base Reflectivity (High Res)",
    "N0U": "Base Radial Velocity (High Res)",
    "N0S": "Storm Relative Radial Velocity",
    "NET": "Echo Tops",
    "N0R": "Base Reflectivity",
    "N0V": "Base Radial Velocity",
    "N0Z": "Base Reflectivity",
    "TR0": "TDWR Base Reflectivity",
    "TV0": "TDWR Radial Velocity",
    "TZL": "TDWR Base Reflectivity",
}


def parse_time(s):
    """
    Convert ISO something into a datetime
    """
    try:
        if len(s) == 17:
            date = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")
        elif len(s) == 20:
            date = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
        else:
            date = datetime.datetime.utcnow()
    except Exception:
        date = datetime.datetime.utcnow()
    return date


def available_radars(fields):
    """
    Return available RADAR sites for the given location and date!
    """
    lat = fields.get("lat", 41.9)
    lon = fields.get("lon", -92.3)
    start_gts = parse_time(fields.get("start", "2012-01-27T00:00Z"))
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()
    root = {"radars": []}
    if lat is None or lon is None:
        sql = """
        select id, name,
        ST_x(geom) as lon, ST_y(geom) as lat, network
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR')
        ORDER by id asc"""
    else:
        sql = f"""
        select id, name, ST_x(geom) as lon, ST_y(geom) as lat, network,
        ST_Distance(geom, GeomFromEWKT('SRID=4326;POINT({lon} {lat})')) as dist
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR')
        and ST_Distance(geom, GeomFromEWKT('SRID=4326;POINT({lon} {lat})')) < 3
        ORDER by dist asc
        """
    mcursor.execute(sql)
    root["radars"].append(
        {
            "id": "USCOMP",
            "name": "National Composite",
            "lat": 42.5,
            "lon": -95,
            "type": "COMPOSITE",
        }
    )
    for row in mcursor:
        radar = row[0]
        if not os.path.isdir(
            start_gts.strftime(
                f"/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/{radar}"
            )
        ):
            continue
        root["radars"].append(
            {
                "id": radar,
                "name": row[1],
                "lat": row[3],
                "lon": row[2],
                "type": row[4],
            }
        )
    mcursor.close()
    pgconn.close()
    return root


def find_scans(root, radar, product, sts, ets):
    """Find scan times with data

    Note that we currently have a 500 length hard coded limit, so if we are
    interested in a long term time period, we should lengthen out our
    interval to look for files

    Args:
      root (dict): where we write our findings to
      radar (string): radar we are interested in
      product (string): NEXRAD product of interest
      sts (datetime): start time to look for data
      ets (datetime): end time to look for data
    """
    now = sts
    times = []
    if radar in ["USCOMP"]:
        # These are every 5 minutes, so 288 per day
        now -= datetime.timedelta(minutes=(now.minute % 5))
        while now < ets:
            if os.path.isfile(
                now.strftime(
                    "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/"
                    f"{product.lower()}_%Y%m%d%H%M.png"
                )
            ):
                times.append({"ts": now.strftime("%Y-%m-%dT%H:%MZ")})
            now += datetime.timedelta(minutes=5)
    else:
        while now < ets:
            if os.path.isfile(
                now.strftime(
                    "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/"
                    f"{radar}/{product}/{radar}_{product}"
                    "_%Y%m%d%H%M.png"
                )
            ):
                times.append({"ts": now.strftime("%Y-%m-%dT%H:%MZ")})
            now += datetime.timedelta(minutes=1)
    if len(times) > 500:
        # Do some filtering
        interval = int((len(times) / 500.0) + 1)
        times = times[::interval]

    root["scans"] = times


def is_realtime(sts):
    """
    Check to see if this time is close to realtime...
    """
    if (datetime.datetime.utcnow() - sts).total_seconds() > 3600:
        return False
    return True


def list_files(fields):
    """
    List available NEXRAD files based on the form request
    """
    radar = fields.get("radar", "DMX")[:10]
    product = fields.get("product", "N0Q")[:3]
    start_gts = parse_time(fields.get("start", "2012-01-27T00:00Z"))
    end_gts = parse_time(fields.get("end", "2012-01-27T01:00Z"))
    # practical limit here of 10 days
    if (start_gts + datetime.timedelta(days=10)) < end_gts:
        end_gts = start_gts + datetime.timedelta(days=10)
    root = {"scans": []}
    find_scans(root, radar, product, start_gts, end_gts)
    if not root["scans"] and is_realtime(start_gts):
        now = start_gts - datetime.timedelta(minutes=10)
        find_scans(root, radar, product, now, end_gts)

    return root


def list_products(fields):
    """
    List available NEXRAD products
    """
    radar = fields.get("radar", "DMX")[:10]
    now = parse_time(fields.get("start", "2012-01-27T00:00Z"))
    root = {"products": []}
    if radar == "USCOMP":
        for dirname in ["N0Q", "N0R"]:
            testfp = now.strftime(
                "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/"
                f"uscomp/{dirname.lower()}_%Y%m%d0000.png"
            )
            if os.path.isfile(testfp):
                root["products"].append(
                    {"id": dirname, "name": NIDS.get(dirname, dirname)}
                )
    else:
        basedir = now.strftime(
            f"/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/{radar}"
        )
        if os.path.isdir(basedir):
            os.chdir(basedir)
            for dirname in glob.glob("???"):
                root["products"].append(
                    {"id": dirname, "name": NIDS.get(dirname, dirname)}
                )
    return root


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    if environ["REQUEST_METHOD"] not in ["GET", "POST"]:
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        data = "Invalid Request"
        return [data.encode("ascii")]

    operation = fields.get("operation", "list")
    callback = fields.get("callback")
    data = ""
    if callback is not None:
        data += f"{html_escape(callback)}("
    if operation == "list":
        data += json.dumps(list_files(fields))
    elif operation == "available":
        data += json.dumps(available_radars(fields))
    elif operation == "products":
        data += json.dumps(list_products(fields))
    if callback is not None:
        data += ")"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
