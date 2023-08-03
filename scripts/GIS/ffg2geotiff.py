"""Generate a GeoTIFF from the FFG product."""
import os
import sys

import pygrib
import pyproj
from pyiem.util import logger, utc

LOG = logger()


def main(argv):
    """Go Main."""
    valid = utc(*[int(i) for i in argv[1:]])
    grbfn = (
        "/mesonet/ARCHIVE/data/"
        f"{valid:%Y/%m/%d}/model/ffg/5kmffg_{valid:%Y%m%d%H}.grib2"
    )
    if not os.path.isfile(grbfn):
        LOG.warning("%s is missing", grbfn)
        return
    grbs = pygrib.open(grbfn)
    pj = None
    for grb in grbs:
        if pj is None:
            pj = pyproj.Proj(grb.projparams)
        # grb.stepRange to get the hour
        print(grb.projparams)


if __name__ == "__main__":
    main(sys.argv)
