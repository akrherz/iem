"""Check a raster file and count the number of non-zero values."""
from __future__ import print_function
import sys

from osgeo import gdal
import numpy


def main():
    """Go Main Go."""
    ntp = gdal.Open("/home/ldm/data/gis/images/4326/USCOMP/ntp_0.png")
    data = ntp.ReadAsArray()
    count = numpy.sum(numpy.where(data > 0, 1, 0))
    sz = data.shape[0] * data.shape[1]

    if count > 1000:
        print("OK - %s/%s|count=%s;100;500;1000" % (count, sz, count))
        status = 0
    elif count > 500:
        print("WARNING - %s/%s|count=%s;100;500;1000" % (count, sz, count))
        status = 1
    else:
        print("CRITICAL - %s/%s|count=%s;100;500;1000" % (count, sz, count))
        status = 2
    return status


if __name__ == "__main__":
    sys.exit(main())
