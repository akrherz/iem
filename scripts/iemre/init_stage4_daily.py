"""Generate the StageIV "daily" file at 12z."""

import os
from datetime import datetime

import click
import numpy as np
from pyiem import stage4
from pyiem.util import logger, ncopen

LOG = logger()
BASEDIR = "/mesonet/data/stage4"


def init_year(ts: datetime, ci: bool) -> str | None:
    """Create a new NetCDF file for a year of our specification!"""
    # Get existing stageIV netcdf file to copy its cordinates from
    tmplnc = ncopen(f"{BASEDIR}/{ts.year}_stage4_hourly.nc", "r")

    fn = f"{BASEDIR}/{ts.year}_stage4_daily.nc"
    if os.path.isfile(fn):
        LOG.info("Cowardly refusing to overwrite %s", fn)
        return None
    nc = ncopen(fn, "w")
    nc.title = f"StageIV 12z-12z Totals for {ts.year}"
    nc.platform = "Grided"
    nc.description = "StageIV"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"  # *cough*
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = "%s Generated" % (datetime.now().strftime("%d %B %Y"),)
    nc.comment = "No Comment at this time"
    # Store projection information
    nc.proj4 = stage4.PROJ.srs

    # Setup Dimensions
    nc.createDimension("x", tmplnc.dimensions["x"].size)
    nc.createDimension("y", tmplnc.dimensions["y"].size)
    nc.createDimension("nv", 2)
    ts2 = datetime(ts.year + 1, 1, 1)
    days = 2 if ci else (ts2 - ts).days
    nc.createDimension("time", int(days))

    x = nc.createVariable("x", float, ("x",))
    x.units = "m"
    x.long_name = "X coordinate of projection"
    x.standard_name = "projection_x_coordinate"
    x.axis = "X"
    x.bounds = "x_bounds"
    x[:] = stage4.XAXIS

    x_bounds = nc.createVariable("x_bounds", float, ("x", "nv"))
    x_bounds[:, 0] = stage4.XAXIS - stage4.DX / 2.0
    x_bounds[:, 1] = stage4.XAXIS + stage4.DX / 2.0

    y = nc.createVariable("y", float, ("y",))
    y.units = "m"
    y.long_name = "Y coordinate of projection"
    y.standard_name = "projection_y_coordinate"
    y.axis = "Y"
    y.bounds = "y_bounds"
    y[:] = stage4.YAXIS

    y_bounds = nc.createVariable("y_bounds", float, ("y", "nv"))
    y_bounds[:, 0] = stage4.YAXIS - stage4.DY / 2.0
    y_bounds[:, 1] = stage4.YAXIS + stage4.DY / 2.0

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", float, ("y", "x"))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    # Grid centers
    lat[:] = tmplnc.variables["lat"][:]

    lon = nc.createVariable("lon", float, ("y", "x"))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = tmplnc.variables["lon"][:]

    tm = nc.createVariable("time", float, ("time",))
    tm.units = f"Days since {ts:%Y}-01-01 12:00:0.0"
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable(
        "p01d_12z", float, ("time", "y", "x"), fill_value=1.0e20
    )
    p01d.units = "mm"
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation at 12z"

    nc.close()
    tmplnc.close()
    return fn


@click.command()
@click.option("--year", type=int, required=True)
@click.option("--ci", is_flag=True, default=False)
def main(year: int, ci: bool) -> None:
    """Go Main"""
    fn = init_year(datetime(year, 1, 1), ci)
    if ci and fn is not None:
        with ncopen(fn, "a") as nc:
            for i in range(2):
                nc.variables["p01d_12z"][i] = (i + 1) * 24.0


if __name__ == "__main__":
    main()
