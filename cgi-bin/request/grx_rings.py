#!/usr/bin/env python
"""Author: Zach Hiris"""
import math
import cgi

from pyiem.util import ssw


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


def main():
    """Go Main Go."""
    form = cgi.FieldStorage()
    ssw("Content-type: application/octet-stream\n")
    ssw(("Content-Disposition: attachment; filename=placefile_rings.txt\n\n"))

    # Things for the user to theoretically input:
    loc = form.getfirst("loc", "Jack Trice Stadium")
    pointLat = float(form.getfirst("lat", 42.014004))
    pointLon = float(form.getfirst("lon", -93.635773))
    ssw(
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
        distanceInMiles = float(form.getfirst("m%s" % (i,), 100))
        if distanceInMiles <= 0.00001:
            continue
        r = int(form.getfirst("r%s" % (i,), 255))
        g = int(form.getfirst("g%s" % (i,), 255))
        b = int(form.getfirst("b%s" % (i,), 0))
        a = int(form.getfirst("a%s" % (i,), 255))

        # Create the lon/lat pairs
        X, Y = createCircleAroundWithRadius(
            pointLat, pointLon, distanceInMiles
        )

        ssw(
            ("Color: %s %s %s %s\n" 'Line: 2, 0, "%.1f miles from %s" \n')
            % (r, g, b, a, distanceInMiles, loc)
        )
        for x, y in zip(X, Y):
            ssw(" %s, %s\n" % (y, x))
        ssw("End:\n\n")


if __name__ == "__main__":
    main()
