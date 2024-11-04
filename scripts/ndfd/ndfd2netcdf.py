"""Copy NDFD grib data to netcdf.

Called from RUN_10_AFTER.sh
"""

import os
from datetime import datetime, timedelta

import click
import numpy as np
import pygrib
from pyiem.util import ncopen, utc


def create_netcdf(ts):
    """Make the file."""
    fn = ts.strftime("/mesonet/data/ndfd/%Y%m%d%H_ndfd.nc")
    nc = ncopen(fn, "w")
    nc.title = "NWS NDFD Forecast From %s" % (ts.strftime("%Y-%m-%dT%H:%MZ"),)
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = "%s Generated" % (utc().strftime("%Y-%m-%dT%H:%MZ"),)

    grbs = pygrib.open(
        "/mesonet/ARCHIVE/data/2019/05/06/model/"
        "ndfd/00/ndfd.t00z.awp2p5f001.grib2"
    )
    grb = grbs[1]
    shape = grb.values.shape
    lats, lons = grb.latlons()
    # Setup dimensions
    nc.createDimension("lat", shape[0])
    nc.createDimension("lon", shape[1])
    nc.createDimension("day", 7)

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("lat", "lon"))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = lats

    lon = nc.createVariable("lon", float, ("lat", "lon"))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = lons

    day = nc.createVariable("day", float, ("day",))
    day.units = "days since %s-01-01" % (ts.year,)
    doy = int(ts.strftime("%j")) - 1
    day[:] = range(doy, doy + 7)

    high = nc.createVariable(
        "high_tmpk", np.uint16, ("day", "lat", "lon"), fill_value=65535
    )
    high.units = "K"
    high.scale_factor = 0.01
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable(
        "low_tmpk", np.uint16, ("day", "lat", "lon"), fill_value=65535
    )
    low.units = "K"
    low.scale_factor = 0.01
    low.long_name = "2m Air Temperature Daily Low"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    p01d = nc.createVariable(
        "p01d", np.uint16, ("day", "lat", "lon"), fill_value=65535
    )
    p01d.units = "mm"
    p01d.scale_factor = 0.01
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()
    return ncopen(fn, "a")


def merge_grib(ts, nc):
    """Merge what grib data we can find into the netcdf file."""
    # taking some liberties here given our hard coded 0z start below
    for fhour in range(6, 169, 6):
        fts = ts + timedelta(hours=fhour)
        fhourstr = "%03i" % (fhour,)
        gribfn = ts.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/ndfd/"
            f"%H/ndfd.t%Hz.awp2p5f{fhourstr}.grib2"
        )
        if not os.path.isfile(gribfn):
            print("ndfd2netcdf missing %s" % (gribfn,))
            continue
        grbs = pygrib.open(gribfn)
        for grb in grbs:
            if (
                grb.valid_key("parameterName")
                and grb["parameterName"] == "Minimum temperature"
            ):
                # This is 12z
                days = int((fts - ts).total_seconds() / 86400)
                nc.variables["low_tmpk"][days, :, :] = grb.values
            elif (
                grb.valid_key("parameterName")
                and grb["parameterName"] == "Maximum temperature"
            ):
                # This is 0z
                days = int((fts - ts).total_seconds() / 86400) - 1
                nc.variables["high_tmpk"][days, :, :] = grb.values
            elif (
                grb.valid_key("parameterName")
                and grb["parameterName"] == "Total precipitation"
            ):
                # This is tricky
                days = (fhour - 6) / 24
                if days < 0:
                    continue
                current = nc.variables["p01d"][days, :, :]
                if current.mask.all():
                    nc.variables["p01d"][days, :, :] = grb.values
                else:
                    nc.variables["p01d"][days, :, :] = current + grb.values


def workflow(ts):
    """Do the work."""
    nc = create_netcdf(ts)
    merge_grib(ts, nc)
    nc.close()


@click.command()
@click.option("--date", "dt", required=True, help="UTC date to process")
def main(dt: datetime):
    """Process a given UTC into netcdf."""
    # TODO: we presently only support the 0z NDFD
    ts = utc(dt.year, dt.month, dt.day)
    workflow(ts)


if __name__ == "__main__":
    main()
