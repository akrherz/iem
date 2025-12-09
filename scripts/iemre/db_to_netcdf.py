"""Copy database grids to netcdf.

    Example: python db_to_netcdf.py <year> <month> <day> <utchour>

If hour and minute are omitted, this is a daily copy, otherwise hourly.

see: akrherz/iem#199
"""

import warnings
from datetime import datetime

import click
import numpy as np
from pyiem import iemre
from pyiem.util import logger, ncopen

# We are going from float64 to uint16, so this appears to be unavoidable
warnings.simplefilter("ignore", RuntimeWarning)
LOG = logger()


@click.command()
@click.option(
    "--date",
    "dt",
    required=True,
    type=click.DateTime(),
    help="Valid timestamp",
)
@click.option("--domain", default="conus", help="Domain to process")
@click.option("--varname", default=None, help="Variable to process")
def main(dt: datetime, domain: str, varname: str | None) -> None:
    """Go Main Go."""
    dt = dt.date()
    ncfn = iemre.get_daily_ncname(dt.year, domain=domain)
    idx = iemre.daily_offset(dt)
    ds = iemre.get_grids(dt, domain=domain, varnames=varname)
    with ncopen(ncfn, "a", timeout=600) as nc:
        for vname in ds:
            if vname not in nc.variables:
                LOG.warning("Variable %s not in netcdf file, skipping", vname)
                continue
            # Careful here, ds could contain NaN values
            nc.variables[vname][idx] = np.ma.array(
                ds[vname].values, mask=np.isnan(ds[vname].values)
            )


if __name__ == "__main__":
    main()
