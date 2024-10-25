""".. title:: Climodat Degree Days service with GFS/NDFD forecast

Return to `API Services </api/#json>`_

Documentation for /json/climodat_dd.py
--------------------------------------

This service emits some degree day data along with forecast from the most
recent GFS and NDFD model runs.  Note that the model forecast data does not
support archived usage.

Changelog
---------

- 2024-08-10: Initial documentation release and pydantic validation

Example Usage
-------------

Get the GDD data for Ames, Iowa from 2023-06-01 to 2023-06-10 with a base of
50 and ceiling of 86 degrees Fahrenheit.

https://mesonet.agron.iastate.edu/json/climodat_dd.py\
?station=IATAME&sdate=2023-06-01&edate=2023-06-10&gddbase=50&gddceil=86

"""

import datetime
import json
import os

import numpy as np
from metpy.units import units
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.iemre import find_ij
from pyiem.meteorology import gdd as calc_gdd
from pyiem.util import c2f, ncopen
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        default=None,
        description="Optional JSONP callback function name.",
    )
    edate: datetime.date = Field(
        ...,
        description="The end date for the period of interest.",
    )
    gddbase: int = Field(
        50,
        description="The base temperature for GDD computation.",
    )
    gddceil: int = Field(
        86,
        description="The ceiling temperature for GDD computation.",
    )
    sdate: datetime.date = Field(
        ...,
        description="The start date for the period of interest.",
    )
    station: str = Field(
        ...,
        description="The station identifier to query.",
        max_length=6,
        min_length=6,
    )


def compute_taxis(ncvar):
    """Figure out our dates."""
    basets = datetime.datetime.strptime(
        ncvar.units[:21], "Days since %Y-%m-%d"
    ).date()
    return [basets + datetime.timedelta(days=val) for val in ncvar[:]]


def compute(taxis, highs, lows, gddbase, gddceil):
    """Sensibly compute gdds."""
    res = []
    total = 0
    vals = calc_gdd(
        units("degF") * highs, units("degF") * lows, gddbase, gddceil
    )
    for dt, val, high, low in zip(taxis, vals, highs, lows):
        if np.ma.is_masked(val):
            continue
        total += val
        res.append(
            {"date": f"{dt:%Y-%m-%d}", "gdd": val, "high": high, "low": low}
        )
    return res, total


def run(station, sdate, edate, gddbase, gddceil):
    """Do something"""
    with get_sqlalchemy_conn("coop") as conn:
        res = conn.execute(
            text("""
            WITH obs as (
                select sum(gddxx(:gddbase, :gddceil, high, low)) from alldata
                where station = :station and day >= :sdate and day <= :edate)
            select o.sum, st_x(t.geom) as lon, st_y(t.geom) as lat
            from obs o, stations t WHERE t.id = :station and sum is not null
            """),
            {
                "station": station,
                "sdate": sdate,
                "edate": edate,
                "gddbase": gddbase,
                "gddceil": gddceil,
            },
        )
        if res.rowcount == 0:
            raise IncompleteWebRequest("No Data Found.")
        accum, lon, lat = [float(x) for x in res.fetchone()]
    data = {
        "station": station,
        "sdate": f"{sdate:%Y-%m-%d}",
        "edate": f"{edate:%Y-%m-%d}",
        "gddbase": gddbase,
        "gddceil": gddceil,
        "accum": accum,
    }
    idx, jdx = find_ij(lon, lat)
    if idx is not None:
        for model in ["gfs", "ndfd"]:
            ncfn = f"/mesonet/data/iemre/{model}_current.nc"
            if not os.path.isfile(ncfn):
                continue
            with ncopen(ncfn) as nc:
                highs = c2f(nc.variables["high_tmpk"][:, jdx, idx] - 273.15)
                lows = c2f(nc.variables["low_tmpk"][:, jdx, idx] - 273.15)
                taxis = compute_taxis(nc.variables["time"])
                gdds, total = compute(taxis, highs, lows, gddbase, gddceil)
                data[model] = gdds
                data[f"{model}_accum"] = total
                data[f"{model}_sdate"] = f"{gdds[0]['date']}"
                data[f"{model}_edate"] = f"{gdds[-1]['date']}"

    return json.dumps(data)


def get_mckey(environ):
    """Get the memcache key."""
    return (
        f"/json/climodat_dd/{environ['station']}/{environ['sdate']}/"
        f"{environ['edate']}/{environ['gddbase']}/{environ['gddceil']}"
    )


@iemapp(
    help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=32200
)
def application(environ, start_response):
    """Answer request."""
    station = environ["station"]
    sdate = environ["sdate"]
    edate = environ["edate"]
    if edate < sdate:
        sdate, edate = edate, sdate
    gddbase = environ["gddbase"]
    gddceil = environ["gddceil"]

    res = run(station, sdate, edate, gddbase, gddceil)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("ascii")
