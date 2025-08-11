"""..title :: Geocoder Service

Proxies to the US Census Geocoding API.

Examples
--------

https://mesonet.agron.iastate.edu/cgi-bin/geocoder.py\
?address=100%20Main%20St%20Ames%20Iowa

https://mesonet.agron.iastate.edu/cgi-bin/geocoder.py\
?street=100%20Main%20St&city=Ames%20Iowa

"""

from io import StringIO

import httpx
from pydantic import Field
from pyiem.webutil import CGIModel, iemapp

SERVICE = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"


class MyModel(CGIModel):
    address: str = Field(None, description="Street address to geocode")
    city: str = Field(None, description="City name to geocode")
    street: str = Field(None, description="Street name to geocode")


@iemapp(help=__doc__, schema=MyModel)
def application(environ, start_response):
    """Go main go"""
    if "address" in environ:
        address = environ["address"].strip()
    elif "street" in environ and "city" in environ:
        address = f"{environ['street']}, {environ['city']}".strip()
    else:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"APIFAIL"]

    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json",
    }
    sio = StringIO()
    try:
        resp = httpx.get(SERVICE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            # Census uses coordinates {"x": lon, "y": lat}
            lat = matches[0]["coordinates"]["y"]
            lon = matches[0]["coordinates"]["x"]
            sio.write(f"{lat},{lon}")
        else:
            sio.write("ERROR")
    except Exception:  # pragma: no cover - defensive, return generic error
        sio.write("ERROR")
    start_response("200 OK", [("Content-type", "text/plain")])
    return [sio.getvalue().encode("ascii")]
