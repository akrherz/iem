""".. service:: IEM Archived RADAR Metadata Service

Return to `JSON Services </json/>`_

Documentation for /json/radar.py
--------------------------------

This service provides metadata about available NEXRAD RADAR data that the
IEM has archived.  The data is stored in a directory structure that is
organized by radar site and product type.  The data is stored in PNG format
and is available for download.

Changelog
---------

- 2024-07-24: Initial documentation release and pydantic validation

Example Usage
-------------

Provide metadata for N0B products for YUX radar between 8 and 10 UTC on
July 24th, 2024:

https://mesonet.agron.iastate.edu/json/radar?operation=list&product=N0B\
&radar=YUX&start=2024-07-24T08:00Z&end=2024-07-24T10:00Z

Provide available RADAR products for the USCOMP (IEM generated mosaic) around
the time 23:35 UTC on July 22nd, 2024:

https://mesonet.agron.iastate.edu/json/radar?radar=USCOMP\
&start=2024-07-22T23:35:00Z&operation=products

Provide an approximation of available RADARs at 26.14N and 80.48W valid at
15:20 UTC on June 30th, 2024:

https://mesonet.agron.iastate.edu/json/radar?lat=26.14&lon=-80.48&\
start=2024-06-30T15:20:00Z&operation=available

"""

import datetime
import glob
import json
import os.path

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

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


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        default=None,
        description="Optional JSONP callback function name",
        max_length=128,
    )
    end: AwareDatetime = Field(
        default=None,
        description="End of time period to search for data",
    )
    lat: float = Field(
        default=41.9,
        description="Latitude of location to search for nearby RADARs",
        ge=-90,
        le=90,
    )
    lon: float = Field(
        default=-92.3,
        description="Longitude of location to search for nearby RADARs",
        ge=-180,
        le=180,
    )
    operation: str = Field(
        default="list",
        description="The operation to perform, either list or available",
        pattern="^(list|available|products)$",
    )
    product: str = Field(
        default="N0Q",
        description="The NEXRAD product to search for data",
        max_length=3,
    )
    radar: str = Field(
        default="DMX",
        description="The RADAR site to search for data",
        max_length=10,
    )
    start: AwareDatetime = Field(
        default=None,
        description="Find RADARs available at the given time, defaults to now",
    )


def available_radars(environ):
    """
    Return available RADAR sites for the given location and date!
    """
    lat = environ["lat"]
    lon = environ["lon"]
    start_gts = environ["start"]
    if start_gts is None:
        start_gts = utc()
    params = {
        "lat": lat,
        "lon": lon,
        "start": start_gts,
    }
    root = {"radars": []}
    if lat is None or lon is None:
        sql = """
        select id, name,
        ST_x(geom) as lon, ST_y(geom) as lat, network
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR')
        ORDER by id asc"""
    else:
        sql = """
        select id, name, ST_x(geom) as lon, ST_y(geom) as lat, network,
        ST_Distance(geom, ST_POINT(:lon, :lat, 4326)) as dist
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR')
        and ST_Distance(geom, ST_POINT(:lon, :lat, 4326)) < 3
        ORDER by dist asc
        """
    root["radars"].append(
        {
            "id": "USCOMP",
            "name": "National Composite",
            "lat": 42.5,
            "lon": -95,
            "type": "COMPOSITE",
        }
    )
    with get_sqlalchemy_conn("mesosite") as pgconn:
        res = pgconn.execute(text(sql), params)
        for row in res:
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
    if (utc() - sts).total_seconds() > 3600:
        return False
    return True


def list_files(environ):
    """
    List available NEXRAD files based on the form request
    """
    radar = environ["radar"]
    product = environ["product"]
    start_gts = environ["start"]
    if start_gts is None:
        start_gts = utc()
    end_gts = environ["end"]
    if end_gts is None:
        end_gts = start_gts + datetime.timedelta(minutes=1)
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
    radar = environ["radar"]
    now = environ["start"]
    if now is None:
        now = utc()
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


def get_mckey(environ: dict) -> str:
    """Get the key."""
    return (
        f"/json/radar.py|{environ['operation']}|{environ['radar']}|"
        f"{environ['product']}|{environ['start']}|{environ['end']}|"
        f"{environ['lat']}|{environ['lon']}"
    ).replace(" ", "")


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=get_mckey,
    memcacheexpire=60,
)
def application(environ, start_response):
    """Answer request."""

    operation = environ["operation"]
    data = ""
    if operation == "list":
        data = json.dumps(list_files(environ))
    elif operation == "available":
        data = json.dumps(available_radars(environ))
    elif operation == "products":
        data = json.dumps(list_products(environ))

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return data.encode("ascii")
