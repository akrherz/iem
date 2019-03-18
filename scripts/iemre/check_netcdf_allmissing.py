"""Generate a report of how many timesteps have all missing data"""
import os
import sys
import glob
import datetime

import numpy as np
from pyiem.util import ncopen, logger

BASEDIR = "/mesonet/data/iemre"
LOG = logger()


def compute_time(nc):
    """Figure out what the time axis is"""
    units = nc.variables['time'].units
    time = nc.variables['time'][:]
    res = []
    if units.startswith('Days since'):
        basets = datetime.datetime.strptime(units[:21], "Days since %Y-%m-%d")
        for val in time:
            res.append(basets + datetime.timedelta(days=val))
    elif units.startswith('Hours since'):
        basets = datetime.datetime.strptime(units[:22],
                                            "Hours since %Y-%m-%d")
        for val in time:
            res.append(basets + datetime.timedelta(hours=val))
    else:
        print("Unknown time unit: %s" % (units, ))
        sys.exit()
    return res


def qc(ncfilename):
    """Go run the QC for this filename"""
    nc = ncopen(ncfilename)
    if 'time' not in nc.variables:
        nc.close()
        return
    LOG("check_netcdf_allmissing: %s", ncfilename)
    taxis = compute_time(nc)
    for vname in nc.variables:
        shape = nc.variables[vname].shape
        if len(shape) != 3:
            continue
        acc = []
        size = shape[1] * shape[2]
        for tstep in range(shape[0]):
            hits = np.sum(nc.variables[vname][tstep].mask)
            if (hits / size) > 0.5:
                acc.append(taxis[tstep])
            else:
                if acc:
                    LOG('   %-16s [%s -> %s] missing', vname, acc[0], acc[-1])
                    acc = []
        if acc:
            LOG('   %-16s [%s -> %s] missing', vname, acc[0], acc[-1])
    nc.close()


def main(argv):
    """Go Main Go"""
    os.chdir(BASEDIR)
    if len(argv) > 1:
        files = argv[1:]
    else:
        files = glob.glob("*.nc")
    for ncfile in files:
        qc(ncfile)


if __name__ == '__main__':
    main(sys.argv)
