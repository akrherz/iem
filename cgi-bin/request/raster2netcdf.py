"""Service providing netcdf files of a requested IEM RASTER

    https://mesonet.agron.iastate.edu/cgi-bin/request/raster2netcdf.py?
    dstr=201710251200&prod=composite_n0r
"""
from io import BytesIO
import os
import datetime
import tempfile

import numpy as np
import pytz
import netCDF4
from PIL import Image
from paste.request import parse_formvars
from pyiem.util import get_dbconn


def get_gridinfo(filename, xpoints, ypoints):
    """Figure out the grid navigation, sigh"""
    with open(f"{filename[:-4]}.wld", encoding="ascii") as fh:
        lines = fh.readlines()
    dx = float(lines[0])
    dy = float(lines[3])
    west = float(lines[4])
    north = float(lines[5])
    south = north + dy * ypoints
    lats = np.arange(0, ypoints) * (0 - dy) + south
    lons = np.arange(0, xpoints) * dx + west
    return lons, lats


def get_table(prod):
    """Return our lookup table"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    xref = [1.0e20] * 256
    cursor.execute(
        "SELECT id, filename_template, units, cf_long_name "
        "from iemrasters where name = %s",
        (prod,),
    )
    (rid, template, units, long_name) = cursor.fetchone()
    cursor.execute(
        """
        SELECT coloridx, value from iemrasters_lookup
        WHERE iemraster_id = %s and value is not null
        ORDER by coloridx ASC
    """,
        (rid,),
    )
    for row in cursor:
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


def do_work(valid, prod, start_response):
    """Our workflow"""
    # Get lookup table
    xref, template, units, long_name = get_table(prod)
    # Get RASTER
    fn = valid.strftime(template)
    if not os.path.isfile(fn):
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: The IEM Archives do not have this file available"
    raster = np.flipud(np.array(Image.open(fn)))
    (ypoints, xpoints) = raster.shape
    # build lat, lon arrays
    lons, lats = get_gridinfo(fn, xpoints, ypoints)
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


def application(environ, start_response):
    """Do great things"""
    form = parse_formvars(environ)
    dstr = form.get("dstr", "201710251200")[:12]
    prod = form.get("prod", "composite_n0r")[:100]  # arb
    valid = datetime.datetime.strptime(dstr, "%Y%m%d%H%M").replace(
        tzinfo=pytz.UTC
    )
    return [do_work(valid, prod, start_response)]
