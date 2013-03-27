"""
 Sample the MERRA solar radiation analysis into estimated values for the
 COOP point archive
 
 1 langley is 41840.00 J m-2 is 41840.00 W s m-2 is 11.622 W hr m-2
 
 So 1000 W m-2 x 3600 is 3,600,000 W s m-2 is 86 langleys
  
 Dr Arritt wants MJ m-2 dy-1
 
"""
import netCDF4
import datetime
import pyproj
import numpy
import iemdb
import sys
import os
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

def get_gp(xc, yc, x, y):
    """ Return the grid point closest to this point """
    distance = []
    xidx = (numpy.abs(xc-x)).argmin()
    yidx = (numpy.abs(yc-y)).argmin()
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
        distance.append( d )
    return gridx, gridy, distance

def do( date ):
    """ Process for a given date 
    6z file has 6z to 9z data
    """
    sts = date.replace(hour=6) # 6z
    ets = sts + datetime.timedelta(days=1)
        
    fn = sts.strftime("/mesonet/merra/%Y/%Y%m%d.nc")
    nc = netCDF4.Dataset( fn )
    rad = nc.variables['swgdn'][7:,:,:]
    cs_rad = nc.variables['swgdnclr'][7:,:,:]
    xc = nc.variables['longitude'][:]
    yc = nc.variables['latitude'][:] 
    nc.close()

    fn2 = ets.strftime("/mesonet/merra/%Y/%Y%m%d.nc")
    nc = netCDF4.Dataset( fn2 )
    rad2 = nc.variables['swgdn'][:7,:,:]
    cs_rad2 = nc.variables['swgdnclr'][:7,:,:]
    nc.close()

    # W m-2 -> J m-2 s-1 -> J m-2 dy-1
    total = (numpy.sum(rad, 0) + numpy.sum(rad2, 0)) * 3600.0
    cs_total = (numpy.sum(cs_rad, 0) + numpy.sum(cs_rad2, 0)) * 3600.0

    ccursor.execute("""
        SELECT station, x(geom), y(geom) from alldata a JOIN stations t on 
        (a.station = t.id) where day = %s and network ~* 'CLIMATE'
        """, (date.strftime("%Y-%m-%d"), ))
    for row in ccursor:
        (x,y) = (row[1], row[2])
        (gridxs, gridys, distances) = get_gp(xc, yc, x, y)

        z0 = total[gridys[0], gridxs[0]]
        z1 = total[gridys[1], gridxs[1]]
        z2 = total[gridys[2], gridxs[2]]
        z3 = total[gridys[3], gridxs[3]]
        
        val = ((z0/distances[0] + z1/distances[1] + z2/distances[2] 
                + z3/distances[3]) / (1./distances[0] + 1./distances[1] + 
                                      1./distances[2] + 1./distances[3] ))
        # MJ m-2 dy-1
        rad_mj = float(val) / 1000000.0
        
        z0 = cs_total[gridys[0], gridxs[0]]
        z1 = cs_total[gridys[1], gridxs[1]]
        z2 = cs_total[gridys[2], gridxs[2]]
        z3 = cs_total[gridys[3], gridxs[3]]
        
        cs_val = ((z0/distances[0] + z1/distances[1] + z2/distances[2] 
                + z3/distances[3]) / (1./distances[0] + 1./distances[1] + 
                                      1./distances[2] + 1./distances[3] ))
        # MJ m-2 dy-1
        cs_rad_mj = float(cs_val) / 1000000.0
        
        if rad_mj < 0:
            print 'WHOA! Negative RAD: %.2f, station: %s' % (rad_mj, row[0])
            continue
        #print "station: %s rad: %.1f" % (row[0], langleys)
        ccursor2.execute("""
        UPDATE alldata_"""+ row[0][:2] +""" SET merra_srad = %s,
        merra_srad_cs = %s WHERE
        day = %s and station = %s
        """, (rad_mj, cs_rad_mj, date.strftime("%Y-%m-%d"), row[0]))
    

do( datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])) )
ccursor2.close()
COOP.commit()
COOP.close()