""".. title :: PRISM Data by Point

Return to `API Services </api/#json>`_

Documentation for /json/prism.py
--------------------------------

This service emits a JSON response of PRISM data for a given point.

Changelog
---------

- 2024-07-24: Initial documentation release and rectify the dates.

Example Usage
-------------

Request PRISM data for January 2024 at a point in Iowa:

https://mesonet.agron.iastate.edu/json/prism.py?lat=41.9&lon=-92.0&\
sdate=2024-01-01&edate=2024-01-31

Request PRISM data for January 10th 2024 at a point in Iowa:

https://mesonet.agron.iastate.edu/json/prism.py?lat=41.9&lon=-92.0&\
valid=2024-01-10

"""

import datetime
import json
import os

import numpy as np
import pandas as pd
from pydantic import Field
from pyiem import prism
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import c2f, mm2inch, ncopen
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function")
    lat: float = Field(41.9, description="Latitude of point", ge=-90, le=90)
    lon: float = Field(
        -92.0, description="Longitude of point", ge=-180, le=180
    )
    valid: datetime.date = Field(
        default=None,
        description="Provide data valid for this date (~12 UTC)",
    )
    sdate: datetime.date = Field(
        default=None,
        description="Inclusive start date for data request",
    )
    edate: datetime.date = Field(
        default=None,
        description="Inclusive end date for data request",
    )


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


def dowork(environ: dict):
    """Do work!"""
    dates = []
    if environ["valid"] is not None:
        dates.append(environ["valid"])
    elif environ["sdate"] is not None and environ["edate"] is not None:
        dates = pd.date_range(environ["sdate"], environ["edate"]).tolist()
    else:
        raise IncompleteWebRequest("Need valid or sdate/edate")

    i, j = prism.find_ij(environ["lon"], environ["lat"])
    if i is None or j is None:
        raise IncompleteWebRequest("Coordinates outside of domain")

    res = {
        "gridi": int(i),
        "gridj": int(j),
        "data": [],
        "disclaimer": (
            "PRISM Climate Group, Oregon State University, "
            "https://prism.oregonstate.edu, created 4 Feb 2004."
        ),
    }

    sidx = prism.daily_offset(dates[0])
    eidx = prism.daily_offset(dates[-1]) + 1

    ncfn = f"/mesonet/data/prism/{dates[0]:%Y}_daily.nc"
    if os.path.isfile(ncfn):
        with ncopen(ncfn) as nc:
            tmax = nc.variables["tmax"][sidx:eidx, j, i]
            tmin = nc.variables["tmin"][sidx:eidx, j, i]
            ppt = nc.variables["ppt"][sidx:eidx, j, i]

        for mt, nt, pt, valid in zip(tmax, tmin, ppt, dates):
            res["data"].append(
                {
                    "valid": valid.strftime("%Y-%m-%dT12:00:00Z"),
                    "high_f": myrounder(c2f(mt), 1),
                    "low_f": myrounder(c2f(nt), 1),
                    "precip_in": myrounder(mm2inch(pt), 2),
                }
            )

    return json.dumps(res)


def get_mckey(environ):
    """get key."""
    return (
        f"/json/prism/{environ['lon']:.2f}/"
        f"{environ['lat']:.2f}/{environ['valid']}/{environ['sdate']}/"
        f"{environ['edate']}"
    )


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=get_mckey,
)
def application(environ, start_response):
    """Answer request."""
    res = dowork(environ)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
