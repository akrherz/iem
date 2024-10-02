""".. title:: Generate a Placefile with Range Rings

Return to `Frontend </request/grx/>`_

This application generates a placefile with range rings around a specified
location. The user can specify the location by entering the latitude and
longitude, the location name, and the filename to save the placefile as.

Author: Zach Hiris

Changelog
---------

- 2024-10-01: Initial documentation update and pydantic validation

Example Requests
----------------

Return a placefile for Solider Field in Chicago with 10, 20, and 30 mile rings.

https://mesonet.agron.iastate.edu/cgi-bin/request/grx_rings.py\
?lat=41.8623&lon=-87.6167&loc=Soldier%20Field&m0=10&m1=20&m2=30

"""

import math
from html import escape
from io import StringIO

from pydantic import Field
from pyiem.util import html_escape
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    fn: str = Field(
        default="placefile_rings.txt", description="Filename to save as"
    )
    lat: float = Field(
        default=42.014004, description="Latitude of center point"
    )
    lon: float = Field(
        default=-93.635773, description="Longitude of center point"
    )
    loc: str = Field(default="Jack Trice Stadium", description="Location name")

    m0: float = Field(
        default=100, description="Distance of first ring in miles", ge=0
    )
    r0: int = Field(
        default=255, description="Red component of color for first ring"
    )
    g0: int = Field(
        default=255, description="Green component of color for first ring"
    )
    b0: int = Field(
        default=0, description="Blue component of color for first ring"
    )
    a0: int = Field(
        default=255, description="Alpha component of color for first ring"
    )
    t0: str = Field(default="", description="Text to display for first ring")

    m1: float = Field(
        default=0, description="Distance of second ring in miles", ge=0
    )
    r1: int = Field(
        default=255, description="Red component of color for second ring"
    )
    g1: int = Field(
        default=255, description="Green component of color for second ring"
    )
    b1: int = Field(
        default=0, description="Blue component of color for second ring"
    )
    a1: int = Field(
        default=255, description="Alpha component of color for second ring"
    )
    t1: str = Field(default="", description="Text to display for second ring")

    m2: float = Field(
        default=0, description="Distance of third ring in miles", ge=0
    )
    r2: int = Field(
        default=255, description="Red component of color for third ring"
    )
    g2: int = Field(
        default=255, description="Green component of color for third ring"
    )
    b2: int = Field(
        default=0, description="Blue component of color for third ring"
    )
    a2: int = Field(
        default=255, description="Alpha component of color for third ring"
    )
    t2: str = Field(default="", description="Text to display for third ring")


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


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go Main Go."""
    fn = escape(environ["fn"])
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}"),
    ]
    start_response("200 OK", headers)

    # Things for the user to theoretically input:
    loc = html_escape(environ["loc"])
    lat = environ["lat"]
    lon = environ["lon"]
    sio = StringIO()
    sio.write(
        f"; This is a placefile to draw a range ring x miles from: {loc}\n"
        "; Created by Zach Hiris - 8/9/2019\n"
        "; Code adapted from Jonathan Scholtes (2016)\n\n\n"
        "Threshold: 999 \n"
        f"Title: Rings @ {loc}\n"
    )

    for i in range(3):
        distanceInMiles = environ[f"m{i}"]
        if distanceInMiles <= 0.00001:
            continue
        r = environ[f"r{i}"]
        g = environ[f"g{i}"]
        b = environ[f"b{i}"]
        a = environ[f"a{i}"]
        t = environ[f"t{i}"].replace("\n", "\\n")

        # Create the lon/lat pairs
        X, Y = createCircleAroundWithRadius(lat, lon, distanceInMiles)
        ll = "\\n" if t != "" else ""
        sio.write(
            f"Color: {r} {g} {b} {a}\n"
            f'Line: 2, 0, "{t}{ll}{distanceInMiles:.1f} miles from {loc}" \n'
        )
        for x, y in zip(X, Y):
            sio.write(f" {y}, {x}\n")
        sio.write("End:\n\n")
    return [sio.getvalue().encode("utf-8")]
