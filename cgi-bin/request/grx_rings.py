"""Author: Zach Hiris"""

import math
from html import escape
from io import StringIO

from pyiem.util import html_escape
from pyiem.webutil import iemapp


def createCircleAroundWithRadius(lat, lon, radiusMiles):
    """Create circle."""
    latArray = []
    lonArray = []

    for brng in range(360):
        lat2, lon2 = getLocation(lat, lon, brng, radiusMiles)
        latArray.append(lat2)
        lonArray.append(lon2)

    return lonArray, latArray


def getLocation(lat1, lon1, brng, distanceMiles):
    """getLocation."""
    lat1 = lat1 * math.pi / 180.0
    lon1 = lon1 * math.pi / 180.0

    # earth radius - If ever needed to be in km vs. miles, change R
    R = 3959
    distanceMiles = distanceMiles / R

    brng = (brng / 90) * math.pi / 2

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distanceMiles)
        + math.cos(lat1) * math.sin(distanceMiles) * math.cos(brng)
    )
    lon2 = lon1 + math.atan2(
        math.sin(brng) * math.sin(distanceMiles) * math.cos(lat1),
        math.cos(distanceMiles) - math.sin(lat1) * math.sin(lat2),
    )
    lon2 = 180.0 * lon2 / math.pi
    lat2 = 180.0 * lat2 / math.pi

    return lat2, lon2


@iemapp()
def application(environ, start_response):
    """Go Main Go."""
    fn = escape(environ.get("fn", "placefile_rings.txt"))
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}"),
    ]
    start_response("200 OK", headers)

    # Things for the user to theoretically input:
    loc = html_escape(environ.get("loc", "Jack Trice Stadium"))
    try:
        lat = environ.get("lat", 42.014004)
        lon = environ.get("lon", -93.635773)
        if isinstance(lat, list):
            lat = lat[0]
        if isinstance(lon, list):
            lon = lon[0]
        pointLat = float(lat)
        pointLon = float(lon)
    except ValueError:
        return [b"ERROR: Invalid lat or lon valid provided."]
    sio = StringIO()
    sio.write(
        f"; This is a placefile to draw a range ring x miles from: {loc}\n"
        "; Created by Zach Hiris - 8/9/2019\n"
        "; Code adapted from Jonathan Scholtes (2016)\n\n\n"
        "Threshold: 999 \n"
        f"Title: Rings @ {loc}\n"
    )

    for i in range(3):
        try:
            distanceInMiles = float(environ.get(f"m{i}", 100))
        except ValueError:
            return [f"ERROR: Invalid m{i} provided.".encode("ascii")]
        if distanceInMiles <= 0.00001:
            continue
        try:
            r = int(float(environ.get(f"r{i}", 255)))
            g = int(float(environ.get(f"g{i}", 255)))
            b = int(float(environ.get(f"b{i}", 0)))
            a = int(float(environ.get(f"a{i}", 255)))
        except ValueError:
            return [b"ERROR: Invalid color provided."]
        t = environ.get(f"t{i}", "").replace("\n", "\\n")

        # Create the lon/lat pairs
        X, Y = createCircleAroundWithRadius(
            pointLat, pointLon, distanceInMiles
        )
        ll = "\\n" if t != "" else ""
        sio.write(
            f"Color: {r} {g} {b} {a}\n"
            f'Line: 2, 0, "{t}{ll}{distanceInMiles:.1f} miles from {loc}" \n'
        )
        for x, y in zip(X, Y):
            sio.write(f" {y}, {x}\n")
        sio.write("End:\n\n")
    return [sio.getvalue().encode("utf-8")]
