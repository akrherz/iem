"""
Return JSON metadata for nexrad information
"""

import datetime
import glob
import json
import os.path

from pyiem.database import get_dbconn
from pyiem.exceptions import BadWebRequest
from pyiem.reference import ISO8601
from pyiem.util import html_escape
from pyiem.webutil import iemapp

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
            date = datetime.datetime.strptime(s, ISO8601)
        else:
            date = datetime.datetime.utcnow()
    except Exception:
        date = datetime.datetime.utcnow()
    return date


def available_radars(environ):
    """
    Return available RADAR sites for the given location and date!
    """
    lat = float(environ.get("lat", 41.9))
    lon = float(environ.get("lon", -92.3))
    if not (-90 < lat < 90 and -180 < lon < 180):
        raise BadWebRequest("Invalid lat/lon provided")
    start_gts = parse_time(environ.get("start", "2012-01-27T00:00Z"))
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
        ST_Distance(geom, ST_POINT({lon}, {lat}, 4326)) as dist
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR')
        and ST_Distance(geom, ST_POINT({lon}, {lat}, 4326)) < 3
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
        now -= datetime.timedelta(minutes=now.minute % 5)
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


def list_files(environ):
    """
    List available NEXRAD files based on the form request
    """
    radar = environ.get("radar", "DMX")[:10]
    product = environ.get("product", "N0Q")[:3]
    start_gts = parse_time(environ.get("start", "2012-01-27T00:00Z"))
    end_gts = parse_time(environ.get("end", "2012-01-27T01:00Z"))
    # practical limit here of 10 days
    if (start_gts + datetime.timedelta(days=10)) < end_gts:
        end_gts = start_gts + datetime.timedelta(days=10)
    root = {"scans": []}
    find_scans(root, radar, product, start_gts, end_gts)
    if not root["scans"] and is_realtime(start_gts):
        now = start_gts - datetime.timedelta(minutes=10)
        find_scans(root, radar, product, now, end_gts)

    return root


def list_products(environ):
    """
    List available NEXRAD products
    """
    radar = environ.get("radar", "DMX")[:10]
    now = parse_time(environ.get("start", "2012-01-27T00:00Z"))
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


@iemapp()
def application(environ, start_response):
    """Answer request."""
    if environ["REQUEST_METHOD"] not in ["GET", "POST"]:
        raise BadWebRequest("Invalid HTTP Method")

    operation = environ.get("operation", "list")
    callback = environ.get("callback")
    data = ""
    if callback is not None:
        data += f"{html_escape(callback)}("
    if operation == "list":
        data += json.dumps(list_files(environ))
    elif operation == "available":
        data += json.dumps(available_radars(environ))
    elif operation == "products":
        data += json.dumps(list_products(environ))
    if callback is not None:
        data += ")"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
