""".. title:: MRMS to ERDAS IMG

This service converts MRMS grib data into a ERDAS IMG file for use in GIS.

Changelog
---------

- 2024-11-01: Migration to pydantic validation.

Example Usage
-------------

Convert the 1 hour MRMS data ending at 18 UTC on 13 April 2016:

https://mesonet.agron.iastate.edu/rainfall/mrms2img.py?\
year=2016&month=4&day=13&hour=18&minute=0&period=1

"""

import tempfile
import zipfile

import numpy as np
from imageio import imread
from osgeo import gdal, osr
from pydantic import Field
from pyiem.exceptions import NoDataFound
from pyiem.util import archive_fetch, utc
from pyiem.webutil import CGIModel, iemapp

# Workaround future
gdal.UseExceptions()


class Schema(CGIModel):
    """See how we are called."""

    year: int = Field(description="Year of the data", default=2016)
    month: int = Field(description="Month of the data", default=4)
    day: int = Field(description="Day of the data", default=13)
    hour: int = Field(description="Hour of the data", default=18)
    minute: int = Field(description="Minute of the data", default=0)
    period: int = Field(description="Period of the data", default=1)


def workflow(tmpdir, valid, period, start_response):
    """Actually do the work!"""
    ppath = valid.strftime(f"%Y/%m/%d/GIS/mrms/p{period}h_%Y%m%d%H%M.png")
    with archive_fetch(ppath) as fn:
        if fn is None:
            raise NoDataFound(f"File not found: {ppath}")
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


@iemapp(schema=Schema, help=__doc__)
def application(environ, start_response):
    """Do Something"""

    valid = utc(
        environ["year"],
        environ["month"],
        environ["day"],
        environ["hour"],
        environ["minute"],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        return [workflow(tmpdir, valid, environ["period"], start_response)]
