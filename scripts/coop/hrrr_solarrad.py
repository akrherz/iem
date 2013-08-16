'''
 Extract HRRR radiation data for storage with COOP data
'''
import psycopg2
import pygrib
import datetime
import pytz
import os
import pyproj
import numpy as np

P4326 = pyproj.Proj(init="epsg:4326")
LCC = pyproj.Proj(("+lon_0=-97.5 +y_0=0.0 +R=6367470. +proj=lcc +x_0=0.0"
                   +" +units=m +lat_2=38.5 +lat_1=38.5 +lat_0=38.5"))


COOP = psycopg2.connect(database='coop', host='iemdb')
cursor = COOP.cursor()
cursor2 = COOP.cursor()

def run( ts ):
    ''' Process data for this timestamp '''
    
    total = None
    xaxis = None
    yaxis = None
    for hr in range(5,23): # Only need 5 AM to 10 PM for solar
        utc = ts.replace(hour=hr).astimezone(pytz.timezone("UTC"))
        fn = utc.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                           +"hrrr.t%Hz.3kmf00.grib2"))
        if not os.path.isfile(fn):
            #print 'HRRR file %s missing' % (fn,)
            continue
        grbs = pygrib.open(fn)
        grb = grbs.select(parameterNumber=192)
        if len(grb) == 0:
            print 'Could not find SWDOWN in HRR %s' % (fn,)
            continue
        g = grb[0]
        if total is None:
            total = g.values
            lat1 = g['latitudeOfFirstGridPointInDegrees']
            lon1 = g['longitudeOfFirstGridPointInDegrees']
            llcrnrx, llcrnry = LCC(lon1,lat1)
            nx = g['Nx']
            ny = g['Ny']
            dx = g['DxInMetres']
            dy = g['DyInMetres']
            xaxis = llcrnrx+dx*np.arange(nx)
            yaxis = llcrnry+dy*np.arange(ny)
        else:
            total += g.values
    
    # Total is the sum of the hourly values
    # We want MJ day-1 m-2
    total = (total * 3600.0) / 1000000.0
    
    cursor.execute("""
        SELECT station, x(geom), y(geom) from alldata a JOIN stations t on 
        (a.station = t.id) where day = %s and network ~* 'CLIMATE'
        """, (ts.strftime("%Y-%m-%d"), ))
    for row in cursor:
        (x,y) = LCC(row[1], row[2])
        i = np.digitize([x], xaxis)[0]
        j = np.digitize([y], yaxis)[0]
        
        rad_mj = float(total[j,i])
        
        if rad_mj < 0:
            print 'WHOA! Negative RAD: %.2f, station: %s' % (rad_mj, row[0])
            continue
        #print "station: %s rad: %.1f" % (row[0], langleys)
        cursor2.execute("""
        UPDATE alldata_"""+ row[0][:2] +""" SET hrrr_srad = %s WHERE
        day = %s and station = %s
        """, (rad_mj, ts.strftime("%Y-%m-%d"), row[0]))
    

if __name__ == '__main__':
    ts = datetime.datetime.utcnow()
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    ts = ts.astimezone(pytz.timezone("America/Chicago"))
    ts = ts - datetime.timedelta(days=1)
    ts = ts.replace(hour=0,minute=0,second=0,microsecond=0)
    
    run( ts )
    cursor.close()
    cursor2.close()
    COOP.commit()
    COOP.close()