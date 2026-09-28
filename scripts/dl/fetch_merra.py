"""
Monthly download of the MERRA data, website suggests that the previous
month is available around the 2-3 week of the next month, so this is run
from RUN_MIDNIGHT.sh, but only on the 28th of each month

MERRA2 Variables we want to process
-----------------------------------
http://goldsmr4.sci.gsfc.nasa.gov/data/MERRA2_MONTHLY/M2TMNXLND.5.12.4/doc/
MERRA2.README.pdf

(M2T1NXRAD)
SWGDNCLR    surface incoming shortwave flux assuming clear sky
SWTDN       toa incoming shortwave flux
SWGDN       surface incoming shortwave flux
SWGDNCLR    surface incoming shortwave flux assuming clear sky

"""

import os
from datetime import datetime, timedelta

import click
import netCDF4
import requests
from pyiem.util import get_properties, logger

LOG = logger()
PROPS = get_properties()


def trans(now):
    """Get the reprocessing level.  Check MERRA docs for changelog."""
    if now.year < 1992:
        return "100"
    if now.year < 2001:
        return "200"
    if now.year < 2011:
        return "300"
    return "400"


def do_month(sts: datetime):
    """Run for a given month"""

    ets = sts + timedelta(days=35)
    ets = ets.replace(day=1)

    interval = timedelta(days=1)
    now = sts
    while now < ets:
        uri = (
            "https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/"
            f"M2T1NXRAD.5.12.4/{now:%Y}/{now:%m}/"
            f"MERRA2_{trans(now)}.tavg1_2d_rad_Nx.{now:%Y%m%d}.nc4"
        )
        dirname = now.strftime("/mesonet/data/merra2/%Y")
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        localfn = now.strftime("/mesonet/data/merra2/%Y/%Y%m%d_tmp.nc")
        resp = requests.get(uri, stream=True, timeout=60)
        with open(localfn, "wb") as f:
            f.writelines(resp.iter_content(chunk_size=8192))
        # Check that the netcdf file is valid
        try:
            nc = netCDF4.Dataset(localfn)
            nc.close()
            os.rename(localfn, localfn.replace("_tmp.nc", ".nc"))
        except Exception:
            LOG.warning("ncopen %s failed, deleting.", localfn)
            os.unlink(localfn)
        now += interval


@click.command()
@click.option("--year", type=int, help="Year to process")
@click.option("--month", type=int, help="Month to process")
def main(year: int | None, month: int | None):
    """Run for last month month"""
    now = datetime.now()
    if year and month:
        now = datetime(year, month, 1)
    else:
        now = now - timedelta(days=35)
        now = now.replace(day=1)
    do_month(now)


if __name__ == "__main__":
    main()
