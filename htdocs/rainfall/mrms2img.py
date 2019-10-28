#!/usr/bin/env python
"""
Create ERDAS Imagine file from a MRMS Raster
"""
import cgi
import os
import datetime
import zipfile

from osgeo import gdal
from osgeo import osr
from imageio import imread
import numpy as np
from pyiem.util import ssw


def workflow(valid, period):
    """ Actually do the work! """
    fn = valid.strftime(
        (
            "/mesonet/ARCHIVE/data/%Y/%m/%d/"
            "GIS/mrms/p" + str(period) + "h_%Y%m%d%H%M.png"
        )
    )
    if not os.path.isfile(fn):
        ssw("Content-type: text/plain\n\n")
        ssw("ERROR: Data File Not Found!")
        return
    img = imread(fn, pilmode="P")
    size = np.shape(img)
    # print 'A', np.max(img), np.min(img), img[0,0], img[-1,-1]
    data = np.ones(size, np.uint16) * 65535

    """
    000 -> 099  0.25mm  000.00 to 024.75
    100 -> 179  1.25mm  025.00 to 123.75
    180 -> 254  5.00mm  125.00 to 495.00
    254                 500.00+
    255  MISSING/BAD DATA
    """
    data = np.where(
        np.logical_and(img >= 180, img < 255),
        (125.0 + (img - 180) * 5.0) * 10,
        data,
    )
    data = np.where(
        np.logical_and(img >= 100, img < 180),
        (25.0 + (img - 100) * 1.25) * 10,
        data,
    )
    # print '2', np.max(data), np.min(data), data[0,0]
    data = np.where(
        np.logical_and(img >= 0, img < 100), (img * 0.25) * 10, data
    )
    # print '4', np.max(data), np.min(data), data[0,0]

    data = data.astype(np.uint16)
    # print '5', np.max(data), np.min(data), data[0,0]

    drv = gdal.GetDriverByName("HFA")
    outfn = "mrms_%sh_%s.img" % (period, valid.strftime("%Y%m%d%H%M"))
    ds = drv.Create(
        outfn, size[1], size[0], 1, gdal.GDT_UInt16, options=["COMPRESS=YES"]
    )
    proj = osr.SpatialReference()
    proj.SetWellKnownGeogCS("EPSG:4326")
    ds.SetProjection(proj.ExportToWkt())
    ds.GetRasterBand(1).WriteArray(data)
    ds.GetRasterBand(1).SetNoDataValue(65535)
    ds.GetRasterBand(1).SetScale(0.1)
    ds.GetRasterBand(1).SetUnitType("mm")
    title = valid.strftime("%s UTC %d %b %Y")
    ds.GetRasterBand(1).SetDescription(
        "MRMS Q3 %sHR Precip Ending %s" % (period, title)
    )
    # Optional, allows ArcGIS to auto show a legend
    ds.GetRasterBand(1).ComputeStatistics(True)
    # top left x, w-e pixel resolution, rotation,
    # top left y, rotation, n-s pixel resolution
    ds.SetGeoTransform([-130.0, 0.01, 0, 55.0, 0, -0.01])
    # close file
    del ds

    zipfn = "mrms_%sh_%s.zip" % (period, valid.strftime("%Y%m%d%H%M"))
    zfp = zipfile.ZipFile(zipfn, "w", zipfile.ZIP_DEFLATED)
    zfp.write(outfn)
    zfp.write(outfn + ".aux.xml")
    zfp.close()

    # Send file back to client
    ssw("Content-type: application/octet/stream\n")
    ssw("Content-Disposition: attachment; filename=%s\n\n" % (zipfn,))
    ssw(open(zipfn, "rb").read())

    os.unlink(outfn)
    os.unlink(zipfn)
    os.unlink(outfn + ".aux.xml")


def main():
    """Do Something"""
    os.chdir("/tmp")

    form = cgi.FieldStorage()
    year = int(form.getfirst("year", 2016))
    month = int(form.getfirst("month", 4))
    day = int(form.getfirst("day", 13))
    hour = int(form.getfirst("hour", 18))
    minute = int(form.getfirst("minute", 0))

    period = int(form.getfirst("period", 1))

    valid = datetime.datetime(year, month, day, hour, minute)

    workflow(valid, period)


if __name__ == "__main__":
    # Go Main Go
    main()
