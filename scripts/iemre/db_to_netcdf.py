"""Copy database grids to netcdf.

    Example: python db_to_netcdf.py <year> <month> <day> <utchour>

If hour and minute are omitted, this is a daily copy, otherwise hourly.

see: akrherz/iem#199
"""
import datetime
import sys

import numpy as np
from pyiem import iemre
from pyiem.util import logger, ncopen, utc

LOG = logger()


def main(argv):
    """Go Main Go."""
    if len(argv) == 6:
        valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
        ncfn = iemre.get_hourly_ncname(valid.year)
        idx = iemre.hourly_offset(valid)
    else:
        valid = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
        ncfn = iemre.get_daily_ncname(valid.year)
        idx = iemre.daily_offset(valid)
    ds = iemre.get_grids(valid)
    with ncopen(ncfn, "a", timeout=600) as nc:
        for vname in ds:
            if vname not in nc.variables:
                continue
            LOG.debug("copying database var %s to netcdf", vname)
            # Careful here, ds could contain NaN values
            nc.variables[vname][idx, :, :] = np.ma.array(
                ds[vname].values, mask=np.isnan(ds[vname].values)
            )


if __name__ == "__main__":
    main(sys.argv)
