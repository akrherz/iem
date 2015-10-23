import urllib
import psycopg2
import numpy as np
import netCDF4
from pyiem.plot import MapPlot

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

total = None
lats = None
lons = None

cursor.execute("""SELECT day, day + '1 day'::interval, high from alldata_ia where station = 'IA2203'
 and high > 99 and month = 8 and day > '1979-01-01' ORDER by day""")
xs = []
ys = []
xx = []
for row in cursor:
    """
    print row
    uri = row[0].strftime(("http://nomads.ncdc.noaa.gov/thredds/ncss/grid/"
            +"narr-a/%Y%m/%Y%m%d/narr-a_221_%Y%m%d_1200_000.grb?var="
            +"Geopotential_height&spatial=all&north=49&west=-104"
            +"&east=-80.5&south=36.0&temporal=all&"
            +"time_start=%Y-%m-%dT12%%3A00%%3A00Z&"
            +"time_end=%Y-%m-%dT15%%3A00%%3A00Z&horizStride=&addLatLon=true"))
    data = urllib.urlopen(uri).read()
    o = open("data/hght12_%s.nc" % (row[0].strftime("%Y%m%d"),), 'w')
    o.write( data )
    o.close()
    """
    
    nc = netCDF4.Dataset("data/hght12_%s.nc" % (row[0].strftime("%Y%m%d"),), 'r')
    idx = np.digitize([500.0], nc.variables['isobaric'][:])[0]
    mslp = nc.variables['Geopotential_height'][0,idx,:,:]
    mx = np.max(mslp[mslp >0])
    if total is None:
        total = mslp
        lats = nc.variables['lat'][:]
        lons = nc.variables['lon'][:]
    else:
        total += mslp
    mlons = lons[mslp==mx]
    mlats = lats[mslp==mx]
    if np.max(mlons) - np.min(mlons) < 10 and np.min(lats) - np.max(lats) < 10:
        xs.append( np.average(mlons) )
        ys.append( np.average(mlats) )
        xx.append('X')
    else:
        print mlons, mlats
        print np.max(mlons) - np.min(mlons), np.min(lats) - np.max(lats)
    nc.close()

m = MapPlot('conus', title='1979-2012 NCEP NARR Composite 500 hPa Geopotential Heights',
            subtitle='12 UTC analysis for %s days in August where Des Moines hit 100+$^\circ$F High' % (cursor.rowcount,))
m.pcolormesh(lons, lats, total / float(cursor.rowcount), np.arange(5650,5951,20),
             units='meters')
#x,y = m.map(xs,ys)
#print xx
m.plot_values(xs,ys, xx, '%s', textsize=16)
m.postprocess(filename='test.png')
