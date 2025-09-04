""".. title:: Raster to NetCDF Data Service

Documentation for /cgi-bin/request/raster2netcdf.py
---------------------------------------------------

The IEM is perhaps more clever than its own good and stores some RASTER data
as the color index value within 8-bit PNG files.  This service converts these
to more conventional NetCDF files with the actual values.

Changelog
---------

- 2025-09-04: Updated docs and testing.
- 2025-09-04: A request for a file resource that does not exist will now
  return a 404 HTTP status code.

Example Usage
-------------

Generate a NetCDF file for the N0R product valid at 2017-10-25 12:00 UTC

https://mesonet.agron.iastate.edu/cgi-bin/request/raster2netcdf.py?\
dstr=201710251200&prod=composite_n0r

"""

import os
import tempfile
from datetime import datetime, timezone
from io import BytesIO

import netCDF4
import numpy as np
from PIL import Image
from pydantic import Field, field_validator
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import archive_fetch
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class Schema(CGIModel):
    """See how we are called."""

    dstr: str = Field(
        "201710251200",
        description="UTC Datetime (YYYYmmddHHMI) to request data for",
        max_length=12,
        pattern=r"^\d{12}$",
    )
    prod: str = Field(..., description="Product to request", max_length=100)

    @field_validator("dstr", mode="before")
    @classmethod
    def validate_dstr(cls, val):
        """Ensure this converts to a datetime."""
        # This will raise a ValueError anyway
        datetime.strptime(val, "%Y%m%d%H%M")
        return val


def get_gridinfo(ppath: str, xpoints, ypoints):
    """Figure out the grid navigation, sigh"""
    with archive_fetch(f"{ppath[:-4]}.wld") as fn:
        if fn is None:
            raise IncompleteWebRequest("No world file found")
        with open(fn) as fh:
            lines = fh.readlines()
    dx = float(lines[0])
    dy = float(lines[3])
    west = float(lines[4])
    north = float(lines[5])
    south = north + dy * ypoints
    lats = np.arange(0, ypoints) * (0 - dy) + south
    lons = np.arange(0, xpoints) * dx + west
    return lons, lats


@with_sqlalchemy_conn("mesosite")
def get_table(prod: str, conn: Connection | None = None):
    """Return our lookup table"""
    res = conn.execute(
        sql_helper("""
    SELECT id, filename_template, units, cf_long_name
    from iemrasters where name = :prod and filename_template is not null
        """),
        {"prod": prod},
    )
    rid = None
    for row in res.mappings():
        rid = row["id"]
        template = row["filename_template"]
        units = row["units"]
        long_name = row["cf_long_name"]
    if rid is None:
        raise IncompleteWebRequest("Unknown prod")
    res = conn.execute(
        sql_helper("""
        SELECT coloridx, value from iemrasters_lookup
        WHERE iemraster_id = :rid and value is not null
        ORDER by coloridx ASC
    """),
        {"rid": rid},
    )
    xref = [1.0e20] * 256
    for row in res:
        xref[row[0]] = row[1]
    return np.array(xref), template, units, long_name


def make_netcdf(xpoints, ypoints, lons, lats):
    """generate the netcdf file"""
    tmpobj = tempfile.NamedTemporaryFile(suffix=".nc", delete=False)
    with netCDF4.Dataset(tmpobj.name, "w") as nc:
        nc.Conventions = "CF-1.6"
        nc.createDimension("lat", ypoints)
        nc.createDimension("lon", xpoints)
        nclon = nc.createVariable("lon", np.float32, ("lon",))
        nclon.units = "degree_east"
        nclon.long_name = "longitude"
        nclon[:] = lons
        nclat = nc.createVariable("lat", np.float32, ("lat",))
        nclat.units = "degree_north"
        nclat.long_name = "latitude"
        nclat[:] = lats
    return tmpobj.name


def do_work(valid: datetime, prod: str, start_response):
    """Our workflow"""
    # Get lookup table
    xref, template, units, long_name = get_table(prod)
    # Get RASTER
    ppath = valid.strftime(template).replace("/mesonet/ARCHIVE/data", "")
    with archive_fetch(ppath) as fh:
        if fh is None:
            start_response(
                "404 File Not Found", [("Content-type", "text/plain")]
            )
            return b"ERROR: The IEM Archives do not have this file available"
        with Image.open(fh) as img:
            raster = np.flipud(np.array(img))
    (ypoints, xpoints) = raster.shape
    # build lat, lon arrays
    lons, lats = get_gridinfo(ppath, xpoints, ypoints)
    # create netcdf file
    tmpname = make_netcdf(xpoints, ypoints, lons, lats)
    with netCDF4.Dataset(tmpname, "a") as nc:
        # write data
        ncvar = nc.createVariable(
            prod, float, ("lat", "lon"), zlib=True, fill_value=1.0e20
        )
        ncvar.units = units
        ncvar.long_name = long_name
        ncvar.coordinates = "lon lat"
        # convert RASTER via lookup table
        ncvar[:] = xref[raster]
    # send data to user
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-disposition", "attachment; filename=res.nc"),
    ]
    start_response("200 OK", headers)
    bio = BytesIO()
    with open(tmpname, "rb") as fh:
        bio.write(fh.read())
    # remove tmp netcdf file
    os.unlink(tmpname)
    return bio.getvalue()


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Do great things"""
    dstr = environ["dstr"]
    prod = environ["prod"]
    valid = datetime.strptime(dstr, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
    return [do_work(valid, prod, start_response)]
