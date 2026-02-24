"""..title :: Geocoder Service

Proxies to the US Census Geocoding API.

Examples
--------

https://mesonet.agron.iastate.edu/cgi-bin/geocoder.py\
?address=100%20Main%20St%20Ames%20Iowa

https://mesonet.agron.iastate.edu/cgi-bin/geocoder.py\
?street=100%20Main%20St&city=Ames%20Iowa

"""

from typing import Annotated

import requests
from pydantic import Field, model_validator
from pyiem.webutil import CGIModel, iemapp

SERVICE = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"


class MyModel(CGIModel):
    address: Annotated[
        str | None, Field(description="Street address to geocode")
    ] = None
    city: Annotated[str | None, Field(description="City name to geocode")] = (
        None
    )
    street: Annotated[
        str | None, Field(description="Street name to geocode")
    ] = None

    @model_validator(mode="after")
    def validate_request(self):
        if not (self.address or (self.street and self.city)):
            raise ValueError(
                "Must provide either 'address' or both 'street' and 'city'"
            )
        return self


def geocode(address: str) -> tuple[float | None, float | None]:
    """Return lat/lon tuple or None if not found."""
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json",
    }
    try:
        resp = requests.get(SERVICE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            # Census uses coordinates {"x": lon, "y": lat}
            lat = matches[0]["coordinates"]["y"]
            lon = matches[0]["coordinates"]["x"]
            return (lat, lon)
    except Exception:  # pragma: no cover - defensive, return generic error
        return (None, None)
    return (None, None)


@iemapp(help=__doc__, schema=MyModel)
def application(environ, start_response):
    """Go main go"""
    if environ["address"]:
        address = environ["address"].strip()
    else:
        address = f"{environ['street']}, {environ['city']}".strip()

    lat, lon = geocode(address)
    start_response("200 OK", [("Content-type", "text/plain")])
    return f"{lat},{lon}" if lat is not None else "ERROR"
