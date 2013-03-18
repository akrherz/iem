"""
 Sample the NARR solar radiation analysis into estimated values for the
 COOP point archive
 
 1 langley is 41840.00 J m-2 is 41840.00 W s m-2 is 11.622 W hr m-2
 
 So 1000 W m-2 x 3600 is 3,600,000 W s m-2 is 86 langleys
 
"""
import netCDF4
import datetime
import pyproj
import numpy
import iemdb
import sys
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

P4326 = pyproj.Proj(init="epsg:4326")
LCC = pyproj.Proj("+lon_0=-107.0 +y_0=0.0 +R=6367470.21484 +proj=lcc +x_0=0.0 +units=m +lat_2=50.0 +lat_1=50.0 +lat_0=50.0")

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
    now = sts
    interval = datetime.timedelta(hours=3)
    while now < ets:
        fn = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/model/NARR/"+
                          "rad_%Y%m%d%H00.nc")
        nc = netCDF4.Dataset( fn )
        rad = nc.variables['Downward_shortwave_radiation_flux'][0,:,:]
        if now == sts:
            xc = nc.variables['x'][:] * 1000.0 # convert to meters
            yc = nc.variables['y'][:] * 1000.0 # convert to meters
        
            total = rad * 10800.0 # 3 hr rad to total rad
        else:
            total += (rad * 10800.0)
        
        nc.close()
        now += interval

    ccursor.execute("""
        SELECT station, x(geom), y(geom) from alldata a JOIN stations t on 
        (a.station = t.id) where day = %s
        """, (date.strftime("%Y-%m-%d"), ))
    for row in ccursor:
        (x,y) = pyproj.transform(P4326, LCC, row[1], row[2])
        (gridxs, gridys, distances) = get_gp(xc, yc, x, y)

        z0 = total[gridys[0], gridxs[0]]
        z1 = total[gridys[1], gridxs[1]]
        z2 = total[gridys[2], gridxs[2]]
        z3 = total[gridys[3], gridxs[3]]
        
        val = ((z0/distances[0] + z1/distances[1] + z2/distances[2] 
                + z3/distances[3]) / (1./distances[0] + 1./distances[1] + 
                                      1./distances[2] + 1./distances[3] ))
        langleys = float(val) / 41840.0
        if langleys < 0:
            print 'WHOA! Negative RAD: %.2f, station: %s' % (langleys, row[0])
            continue
        
        ccursor2.execute("""
        UPDATE alldata_"""+ row[0][:2] +""" SET narr_srad = %s WHERE
        day = %s and station = %s
        """, (langleys, date.strftime("%Y-%m-%d"), row[0]))
    

do( datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])) )
ccursor2.close()
COOP.commit()
COOP.close()