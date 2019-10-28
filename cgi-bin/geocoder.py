#!/usr/bin/env python
"""
 Geocoder used by:
  - IEM Rainfall App
"""
import cgi

import requests
from pyiem.util import ssw, get_properties

SERVICE = "https://maps.googleapis.com/maps/api/geocode/json"


def main():
    """Go main go"""
    props = get_properties()
    form = cgi.FieldStorage()
    if "address" in form:
        address = form["address"].value
    elif "street" in form and "city" in form:
        address = "%s, %s" % (form["street"].value, form["city"].value)
    else:
        ssw("APIFAIL")
        return

    req = requests.get(
        SERVICE,
        params=dict(
            address=address, key=props["google.maps.key2"], sensor="true"
        ),
        timeout=10,
    )
    data = req.json()
    if data["results"]:
        ssw(
            "%s,%s"
            % (
                data["results"][0]["geometry"]["location"]["lat"],
                data["results"][0]["geometry"]["location"]["lng"],
            )
        )
    else:
        ssw("ERROR")


if __name__ == "__main__":
    ssw("Content-type: text/plain \n\n")
    try:
        main()
    except Exception as exp:
        ssw("ERROR\n")
