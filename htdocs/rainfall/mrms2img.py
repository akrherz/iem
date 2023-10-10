"""
Create ERDAS Imagine file from a MRMS Raster
"""
import datetime
import os
import sys
import tempfile
import zipfile

import numpy as np
from imageio import imread
from osgeo import gdal, osr
from paste.request import parse_formvars

# Workaround future
gdal.UseExceptions()


def workflow(tmpdir, valid, period, start_response):
    """Actually do the work!"""
    fn = valid.strftime(
        f"/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/mrms/p{period}h_%Y%m%d%H%M.png"
    )
    if not os.path.isfile(fn):
        raise FileNotFoundError(fn)
    img = imread(fn, pilmode="P")
    size = np.shape(img)
    # print 'A', np.max(img), np.min(img), img[0,0], img[-1,-1]
    data = np.ones(size, np.uint16) * 65535

    # 000 -> 099  0.25mm  000.00 to 024.75
    # 100 -> 179  1.25mm  025.00 to 123.75
    # 180 -> 254  5.00mm  125.00 to 495.00
    # 254                 500.00+
    # 255  MISSING/BAD DATA
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
    data = np.where(
        np.logical_and(img >= 0, img < 100), (img * 0.25) * 10, data
    )

    data = data.astype(np.uint16)

    drv = gdal.GetDriverByName("HFA")
    basefn = f"mrms_{period}h_{valid:%Y%m%d%H%M}"
    outfn = f"{tmpdir}/{basefn}.img"
    proj = osr.SpatialReference()
    proj.SetWellKnownGeogCS("EPSG:4326")
    ds = drv.Create(
        outfn, size[1], size[0], 1, gdal.GDT_UInt16, options=["COMPRESS=YES"]
    )
    ds.SetProjection(proj.ExportToWkt())
    ds.GetRasterBand(1).WriteArray(data)
    ds.GetRasterBand(1).SetNoDataValue(65535)
    ds.GetRasterBand(1).SetScale(0.1)
    ds.GetRasterBand(1).SetUnitType("mm")
    title = valid.strftime("%s UTC %d %b %Y")
    ds.GetRasterBand(1).SetDescription(
        f"MRMS {period}HR Precip Ending {title}"
    )
    # Optional, allows ArcGIS to auto show a legend
    ds.GetRasterBand(1).ComputeStatistics(True)
    # top left x, w-e pixel resolution, rotation,
    # top left y, rotation, n-s pixel resolution
    ds.SetGeoTransform([-130.0, 0.01, 0, 55.0, 0, -0.01])
    ds.FlushCache()
    del ds

    zipfn = f"{tmpdir}/{basefn}.zip"
    with zipfile.ZipFile(zipfn, "w", zipfile.ZIP_DEFLATED) as zfp:
        zfp.write(outfn, f"{basefn}.img")
        zfp.write(f"{outfn}.aux.xml", f"{basefn}.img.aux.xml")

    # Send file back to client
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={basefn}.zip"),
    ]
    start_response("200 OK", headers)
    with open(zipfn, "rb") as fh:
        payload = fh.read()
    return payload


def application(environ, start_response):
    """Do Something"""
    form = parse_formvars(environ)
    year = int(form.get("year", 2016))
    month = int(form.get("month", 4))
    day = int(form.get("day", 13))
    hour = int(form.get("hour", 18))
    minute = int(form.get("minute", 0))

    period = int(form.get("period", 1))

    valid = datetime.datetime(year, month, day, hour, minute)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            return [workflow(tmpdir, valid, period, start_response)]
    except Exception as exp:
        sys.stderr.write(str(exp) + "\n")
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        return [b"An error occurred."]
