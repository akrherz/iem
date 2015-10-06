"""
 Sample the NARR solar radiation analysis into estimated values for the
 COOP point archive

 1 langley is 41840.00 J m-2 is 41840.00 W s m-2 is 11.622 W hr m-2

 So 1000 W m-2 x 3600 is 3,600,000 W s m-2 is 86 langleys

 Updated: to match other columns, we are storing in MJ/day/m2 now!

 26 Jun 1988 is bad!


 http://rda.ucar.edu/dataset/ds608.0

Updates of NARR data from April 1, 2009 to January 31, 2015
released by NCEP have been archived as "rerun4" version of ds608.0
dataset in rda.ucar.edu in May 2015.  This update fixes the codes
that read Mexican precipitation data and a bug introduced when NCEP
switched the computer systems. The direct effects of these changes
are in the precipitation and in the soil moisture fields.

Review the following pdf file for details.
    http://rda.ucar.edu/datasets/ds608.0/docs/rr4.pdf

"""
import netCDF4
import pygrib
import datetime
import pyproj
import numpy as np
import psycopg2
import sys
import os
COOP = psycopg2.connect(database='coop', host='iemdb')
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

P4326 = pyproj.Proj(init="epsg:4326")
LCC = pyproj.Proj(("+lon_0=-107.0 +y_0=0.0 +R=6367470.21484 +proj=lcc "
                   "+x_0=0.0 +units=m +lat_2=50.0 +lat_1=50.0 +lat_0=50.0"))
NC_MODE, GRIB_MODE = range(2)


def get_gp2(lons, lats, lon, lat):
    """ Return the grid points closest to this point """
    dist = ((lons - lon)**2 + (lats - lat)**2)**0.5
    (xidx, yidx) = np.unravel_index(dist.argmin(), dist.shape)
    dx = lon - lons[xidx, yidx]
    dy = lat - lats[xidx, yidx]
    movex = -1
    if dx >= 0:
        movex = 1
    movey = -1
    if dy >= 0:
        movey = 1
    gridx = [xidx, xidx+movex, xidx+movex, xidx]
    gridy = [yidx, yidx, yidx+movey, yidx+movey]
    distance = []
    for myx, myy in zip(gridx, gridy):
        d = ((lat - lats[myx, myy])**2 + (lon - lons[myx, myx])**2)**0.5
        distance.append(d)
    return gridx, gridy, distance


def get_gp(xc, yc, x, y):
    """ Return the grid point closest to this point """
    distance = []
    xidx = (np.abs(xc-x)).argmin()
    yidx = (np.abs(yc-y)).argmin()
    dx = x - xc[xidx]
    dy = y - yc[yidx]
    movex = -1
    if dx >= 0:
        movex = 1
    movey = -1
    if dy >= 0:
        movey = 1
    gridx = [xidx, xidx+movex, xidx+movex, xidx]
    gridy = [yidx, yidx, yidx+movey, yidx+movey]
    for myx, myy in zip(gridx, gridy):
        d = ((y - yc[myy])**2 + (x - xc[myx])**2)**0.5
        distance.append(d)
    return gridx, gridy, distance


def do(date):
    """ Process for a given date
    6z file has 6z to 9z data
    """
    sts = date.replace(hour=6)  # 6z
    ets = sts + datetime.timedelta(days=1)
    now = sts
    interval = datetime.timedelta(hours=3)
    mode = NC_MODE
    lats, lons = None, None
    while now < ets:
        # See if we have Grib data first
        fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/NARR/"
                           "rad_%Y%m%d%H00.grib"))
        if os.path.isfile(fn):
            mode = GRIB_MODE
            grb = pygrib.open(fn)[1]
            if lats is None:
                lats, lons = grb.latlons()
                total = grb['values'] * 10800.0
            else:
                total += (grb['values'] * 10800.0)
            now += interval
            continue
        fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/NARR/"
                           "rad_%Y%m%d%H00.nc"))
        if not os.path.isfile(fn):
            print 'MISSING NARR: %s' % (fn,)
            sys.exit()
        nc = netCDF4.Dataset(fn)
        rad = nc.variables['Downward_shortwave_radiation_flux'][0, :, :]
        if now == sts:
            xc = nc.variables['x'][:] * 1000.0  # convert to meters
            yc = nc.variables['y'][:] * 1000.0  # convert to meters

            total = rad * 10800.0  # 3 hr rad to total rad
        else:
            total += (rad * 10800.0)
        nc.close()
        now += interval

    ccursor.execute("""
        SELECT station, ST_x(geom), ST_y(geom) from
        alldata a JOIN stations t on
        (a.station = t.id) where day = %s
        """, (date.strftime("%Y-%m-%d"), ))
    for row in ccursor:
        if mode == NC_MODE:
            (x, y) = pyproj.transform(P4326, LCC, row[1], row[2])
            (gridxs, gridys, distances) = get_gp(xc, yc, x, y)
        else:
            # Note the hacky reversing of grid coords
            (gridys, gridxs, distances) = get_gp2(lons, lats, row[1], row[2])

        z0 = total[gridys[0], gridxs[0]]
        z1 = total[gridys[1], gridxs[1]]
        z2 = total[gridys[2], gridxs[2]]
        z3 = total[gridys[3], gridxs[3]]

        val = ((z0/distances[0] + z1/distances[1] + z2/distances[2] +
                z3/distances[3]) / (1./distances[0] + 1./distances[1] +
                                    1./distances[2] + 1./distances[3]))
        rad_mj = float(val) / 1000000.0
        if rad_mj < 0:
            print 'WHOA! Negative RAD: %.2f, station: %s' % (rad_mj, row[0])
            continue
        if np.isnan(rad_mj):
            print('NARR SRAD is NaN, station: %s' % (row[0], ))
            rad_mj = None

        ccursor2.execute("""
        UPDATE alldata_""" + row[0][:2] + """ SET narr_srad = %s WHERE
        day = %s and station = %s
        """, (rad_mj, date.strftime("%Y-%m-%d"), row[0]))


if __name__ == '__main__':
    if len(sys.argv) == 4:
        do(datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                             int(sys.argv[3])))
    if len(sys.argv) == 3:
        # Run for a given month!
        sts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), 1)
        ets = sts + datetime.timedelta(days=45)
        ets = ets.replace(day=1)
        now = sts
        while now < ets:
            do(now)
            now += datetime.timedelta(days=1)
    ccursor2.close()
    COOP.commit()
    COOP.close()
