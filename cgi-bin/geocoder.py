"""
Geocoder used by:
 - IEM Rainfall App
"""

from io import StringIO

import requests
from pyiem.util import get_properties
from pyiem.webutil import iemapp

SERVICE = "https://maps.googleapis.com/maps/api/geocode/json"


@iemapp()
def application(environ, start_response):
    """Go main go"""
    props = get_properties()
    if "address" in environ:
        address = environ["address"]
    elif "street" in environ and "city" in environ:
        address = "%s, %s" % (environ["street"], environ["city"])
    else:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"APIFAIL"]

    req = requests.get(
        SERVICE,
        params=dict(
            address=address, key=props["google.maps.key2"], sensor="true"
        ),
        timeout=10,
    )
    data = req.json()
    sio = StringIO()
    if data["results"]:
        sio.write(
            "%s,%s"
            % (
                data["results"][0]["geometry"]["location"]["lat"],
                data["results"][0]["geometry"]["location"]["lng"],
            )
        )
    else:
        sio.write("ERROR")
    start_response("200 OK", [("Content-type", "text/plain")])
    return [sio.getvalue().encode("ascii")]
