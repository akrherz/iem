"""Do the gridding of Solar Radiation Data

Called from RUN_MIDNIGHT.sh
"""
from __future__ import print_function
import datetime
import os
import subprocess
import sys

import pyproj
import pytz
import numpy as np
from scipy.interpolate import NearestNDInterpolator
import pygrib
from pyiem import iemre
from pyiem.util import get_dbconn, utc, ncopen

P4326 = pyproj.Proj(init="epsg:4326")
SWITCH_DATE = utc(2014, 10, 10, 20)


def do_coop(ts):
    """Use COOP solar radiation data"""
    pgconn = get_dbconn("coop", user="nobody")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT ST_x(geom), ST_y(geom),
        coalesce(narr_srad, merra_srad) from alldata a JOIN stations t
        ON (a.station = t.id) WHERE
        day = %s and t.network ~* 'CLIMATE' and substr(id, 3, 1) != 'C'
        and substr(id, 3, 4) != '0000'
    """,
        (ts.strftime("%Y-%m-%d"),),
    )
    lons = []
    lats = []
    vals = []
    for row in cursor:
        if row[2] is None or row[2] < 0:
            continue
        lons.append(row[0])
        lats.append(row[1])
        vals.append(row[2])

    nn = NearestNDInterpolator(
        (np.array(lons), np.array(lats)), np.array(vals)
    )
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)

    ds = iemre.get_grids(ts.date(), varnames="rsds")
    # Convert MJ/d to Wm2
    ds["rsds"].values = nn(xi, yi) * 1000000.0 / 86400.0
    iemre.set_grids(ts.date(), ds)
    subprocess.call(
        "python db_to_netcdf.py %s" % (ts.strftime("%Y %m %d"),), shell=True
    )


def try_merra(ts):
    """Attempt to use MERRA data."""
    # Our files are UTC date based :/
    ncfn1 = ts.strftime("/mesonet/merra2/%Y/%Y%m%d.nc")
    ncfn2 = (ts + datetime.timedelta(days=1)).strftime(
        "/mesonet/merra2/%Y/%Y%m%d.nc"
    )
    if not os.path.isfile(ncfn1) or not os.path.isfile(ncfn2):
        return False
    with ncopen(ncfn1) as nc:
        # Total up from 6z to end of file for today
        total = np.sum(nc.variables["SWGDN"][5:, :, :], axis=0)
    with ncopen(ncfn2) as nc:
        lat1d = nc.variables["lat"][:]
        lon1d = nc.variables["lon"][:]
        # Total up to 6z
        total += np.sum(nc.variables["SWGDN"][:6, :, :], axis=0)

    # We wanna store as W m-2, so we just average out the data by hour
    total = total / 24.0

    lons, lats = np.meshgrid(lon1d, lat1d)
    nn = NearestNDInterpolator(
        (lons.flatten(), lats.flatten()), total.flatten()
    )
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)

    ds = iemre.get_grids(ts.date(), varnames="rsds")
    ds["rsds"].values = nn(xi, yi)
    iemre.set_grids(ts.date(), ds)
    subprocess.call(
        "python db_to_netcdf.py %s" % (ts.strftime("%Y %m %d"),), shell=True
    )

    return True


def do_hrrr(ts):
    """Convert the hourly HRRR data to IEMRE grid"""
    LCC = pyproj.Proj(
        (
            "+lon_0=-97.5 +y_0=0.0 +R=6367470. +proj=lcc +x_0=0.0"
            " +units=m +lat_2=38.5 +lat_1=38.5 +lat_0=38.5"
        )
    )
    total = None
    xaxis = None
    yaxis = None
    # So IEMRE is storing data from coast to coast, so we should be
    # aggressive about running for an entire calendar date
    now = ts.replace(hour=1)
    for _ in range(24):
        now += datetime.timedelta(hours=1)
        utcnow = now.astimezone(pytz.UTC)
        fn = utcnow.strftime(
            (
                "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                "hrrr.t%Hz.3kmf00.grib2"
            )
        )
        if not os.path.isfile(fn):
            continue
        grbs = pygrib.open(fn)
        try:
            if utcnow >= SWITCH_DATE:
                grb = grbs.select(name="Downward short-wave radiation flux")
            else:
                grb = grbs.select(parameterNumber=192)
        except ValueError:
            # don't complain about late evening no-solar
            if utcnow.hour > 10 and utcnow.hour < 24:
                print("iemre/grid_rsds.py %s had no solar rad" % (fn,))
            continue
        if not grb:
            print("Could not find SWDOWN in HRR %s" % (fn,))
            continue
        g = grb[0]
        if total is None:
            total = g.values
            lat1 = g["latitudeOfFirstGridPointInDegrees"]
            lon1 = g["longitudeOfFirstGridPointInDegrees"]
            llcrnrx, llcrnry = LCC(lon1, lat1)
            nx = g["Nx"]
            ny = g["Ny"]
            dx = g["DxInMetres"]
            dy = g["DyInMetres"]
            xaxis = llcrnrx + dx * np.arange(nx)
            yaxis = llcrnry + dy * np.arange(ny)
        else:
            total += g.values

    if total is None:
        print(
            ("iemre/grid_rsds.py found no HRRR data for %s")
            % (ts.strftime("%d %b %Y"),)
        )
        return

    # We wanna store as W m-2, so we just average out the data by hour
    total = total / 24.0

    ds = iemre.get_grids(ts.date(), varnames="rsds")
    for i, lon in enumerate(iemre.XAXIS):
        for j, lat in enumerate(iemre.YAXIS):
            (x, y) = LCC(lon, lat)
            i2 = np.digitize([x], xaxis)[0]
            j2 = np.digitize([y], yaxis)[0]
            try:
                ds["rsds"].values[j, i] = total[j2, i2]
            except IndexError:
                continue

    iemre.set_grids(ts.date(), ds)
    subprocess.call(
        "python db_to_netcdf.py %s" % (ts.strftime("%Y %m %d"),), shell=True
    )


def main(argv):
    """Go Main Go"""
    queue = []
    if len(sys.argv) == 3:
        now = datetime.datetime(int(argv[1]), int(argv[2]), 1, 12)
        while now.month == int(argv[2]):
            queue.append(now)
            now += datetime.timedelta(days=1)
    elif len(sys.argv) == 4:
        sts = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]), 12)
        queue.append(sts)
    else:
        sts = datetime.datetime.now() - datetime.timedelta(days=1)
        sts = sts.replace(hour=12)
        queue.append(sts)
    for sts in queue:
        sts = sts.replace(tzinfo=pytz.timezone("America/Chicago"))
        if not try_merra(sts):
            if sts.year >= 2014:
                do_hrrr(sts)
            else:
                do_coop(sts)


if __name__ == "__main__":
    main(sys.argv)
