"""Download an hour worth of ERA5.

Run from RUN_12Z.sh for 5 days ago.
"""
from datetime import timedelta
import os
import sys

import numpy as np
from pyiem import iemre
from pyiem.util import utc, ncopen, logger
import cdsapi
import pygrib

LOG = logger()
CDSVARS = (
    "10m_u_component_of_wind 10m_v_component_of_wind 2m_dewpoint_temperature "
    "2m_temperature soil_temperature_level_1 soil_temperature_level_2 "
    "soil_temperature_level_3 soil_temperature_level_4 "
    "surface_solar_radiation_downwards total_evaporation total_precipitation "
    "volumetric_soil_water_layer_1 volumetric_soil_water_layer_2 "
    "volumetric_soil_water_layer_3 volumetric_soil_water_layer_4"
).split()


def ingest(grbfn, valid):
    """Consume this grib file."""
    ncfn = f"/mesonet/data/era5/{valid.year}_era5land_hourly.nc"
    grbs = pygrib.open(grbfn)
    ames_i = int((-93.61 - iemre.WEST) * 10)
    ames_j = int((41.99 - iemre.SOUTH) * 10)
    # Eh
    tidx = iemre.hourly_offset(valid)
    with ncopen(ncfn, "a") as nc:
        nc.variables["uwnd"][tidx, :, :] = grbs[1].values
        LOG.info("uwnd %s", nc.variables["uwnd"][tidx, ames_j, ames_i])
        nc.variables["vwnd"][tidx, :, :] = grbs[2].values
        LOG.info("vwnd %s", nc.variables["vwnd"][tidx, ames_j, ames_i])
        nc.variables["dwpk"][tidx, :, :] = grbs[3].values
        LOG.info("dwpf %s", nc.variables["dwpk"][tidx, ames_j, ames_i])
        nc.variables["tmpk"][tidx, :, :] = grbs[4].values
        LOG.info("tmpk %s", nc.variables["tmpk"][tidx, ames_j, ames_i])
        nc.variables["soilt"][tidx, 0, :, :] = grbs[5].values
        nc.variables["soilt"][tidx, 1, :, :] = grbs[6].values
        nc.variables["soilt"][tidx, 2, :, :] = grbs[7].values
        nc.variables["soilt"][tidx, 3, :, :] = grbs[8].values
        LOG.info("soilt %s", nc.variables["soilt"][tidx, :, ames_j, ames_i])
        # -- Solar Radiation is accumulated since 0z
        rsds = nc.variables["rsds"]
        p01m = nc.variables["p01m"]
        evap = nc.variables["evap"]
        val = grbs[9].values
        if valid.hour == 0:
            tidx0 = iemre.hourly_offset((valid - timedelta(hours=24)))
            tsolar = np.sum(rsds[(tidx0 + 1) : tidx], 0) * 3600.0
            tp01m = np.sum(p01m[(tidx0 + 1) : tidx], 0)
            tevap = np.sum(evap[(tidx0 + 1) : tidx], 0)
        elif valid.hour > 1:
            tidx0 = iemre.hourly_offset(valid.replace(hour=1))
            tsolar = np.sum(rsds[tidx0:tidx], 0) * 3600.0
            tp01m = np.sum(p01m[tidx0:tidx], 0)
            tevap = np.sum(evap[tidx0:tidx], 0)
        else:
            tsolar = np.zeros(val.shape)
            tp01m = np.zeros(val.shape)
            tevap = np.zeros(val.shape)
        # J m-2 to W/m2
        newval = (val - tsolar) / 3600.0
        nc.variables["rsds"][tidx, :, :] = np.where(newval < 0, 0, newval)
        LOG.info(
            "rsds nc:%s tsolar:%s grib:%s",
            nc.variables["rsds"][tidx, ames_j, ames_i],
            tsolar[ames_j, ames_i],
            val[ames_j, ames_i],
        )
        # m to mm
        val = grbs[10].values
        nc.variables["evap"][tidx, :, :] = (val * 1000.0) - tevap
        LOG.info(
            "evap %s grib:%s",
            nc.variables["evap"][tidx, ames_j, ames_i],
            val[ames_j, ames_i],
        )
        # m to mm
        val = grbs[11].values
        accum = (val * 1000.0) - tp01m
        nc.variables["p01m"][tidx, :, :] = np.where(accum < 0, 0, accum)
        LOG.info(
            "p01m %s grib:%s",
            nc.variables["p01m"][tidx, ames_j, ames_i],
            val[ames_j, ames_i],
        )
        val = grbs[12].values
        nc.variables["soilm"][tidx, 0, :, :] = val
        nc.variables["soilm"][tidx, 1, :, :] = grbs[13].values
        nc.variables["soilm"][tidx, 2, :, :] = grbs[14].values
        nc.variables["soilm"][tidx, 3, :, :] = grbs[15].values
        LOG.info(
            "soilm %s grib1:%s",
            nc.variables["soilm"][tidx, :, ames_j, ames_i],
            val[ames_j, ames_i],
        )


def run(valid):
    """Run for the given valid time."""
    LOG.info("Running for %s", valid)
    grbfn = f"{valid:%Y%m%d%H}.grib"

    cds = cdsapi.Client(quiet=True)

    cds.retrieve(
        "reanalysis-era5-land",
        {
            "variable": CDSVARS,
            "year": f"{valid.year}",
            "month": f"{valid.month}",
            "day": f"{valid.day}",
            "time": f"{valid:%H}:00",
            "area": [
                iemre.NORTH,
                iemre.WEST,
                iemre.SOUTH,
                iemre.EAST,
            ],
            "format": "grib",
        },
        grbfn,
    )
    ingest(grbfn, valid)
    os.unlink(grbfn)


def main(argv):
    """Go!"""
    if len(argv) == 5:
        valid = utc(*[int(a) for a in argv[1:]])
        run(valid)
    elif len(argv) == 4:
        valid = utc(*[int(a) for a in argv[1:]])
        for hr in range(24):
            run(valid.replace(hour=hr))


if __name__ == "__main__":
    main(sys.argv)
