"""Author: Zach Hiris"""
import math
from html import escape
from io import StringIO

from paste.request import parse_formvars
from pyiem.util import html_escape


def createCircleAroundWithRadius(lat, lon, radiusMiles):
    """Create circle."""
    latArray = []
    lonArray = []

    for brng in range(0, 360):
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


def application(environ, start_response):
    """Go Main Go."""
    form = parse_formvars(environ)
    fn = escape(form.get("fn", "placefile_rings.txt"))
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}"),
    ]
    start_response("200 OK", headers)

    # Things for the user to theoretically input:
    loc = html_escape(form.get("loc", "Jack Trice Stadium"))
    pointLat = float(form.get("lat", 42.014004))
    pointLon = float(form.get("lon", -93.635773))
    sio = StringIO()
    sio.write(
        (
            "; This is a placefile to draw a range ring x miles from: %s\n"
            "; Created by Zach Hiris - 8/9/2019\n"
            "; Code adapted from Jonathan Scholtes (2016)\n\n\n"
            "Threshold: 999 \n"
            "Title: Rings @ %s\n"
        )
        % (loc, loc)
    )

    for i in range(3):
        distanceInMiles = float(form.get("m%s" % (i,), 100))
        if distanceInMiles <= 0.00001:
            continue
        r = int(form.get("r%s" % (i,), 255))
        g = int(form.get("g%s" % (i,), 255))
        b = int(form.get("b%s" % (i,), 0))
        a = int(form.get("a%s" % (i,), 255))
        t = form.get("t%s" % (i,), "").replace("\n", "\\n")

        # Create the lon/lat pairs
        X, Y = createCircleAroundWithRadius(
            pointLat, pointLon, distanceInMiles
        )

        sio.write(
            ("Color: %s %s %s %s\n" 'Line: 2, 0, "%s%s%.1f miles from %s" \n')
            % (r, g, b, a, t, "\\n" if t != "" else "", distanceInMiles, loc)
        )
        for x, y in zip(X, Y):
            sio.write(" %s, %s\n" % (y, x))
        sio.write("End:\n\n")
    return [sio.getvalue().encode("ascii")]
