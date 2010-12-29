# IEMRAIN hourly data gridder

import lib
import os, mx.DateTime, numpy, Ngl, pg, math
from osgeo import gdal
from pyIEM import mesonet

def do(ts):
    """
    Grid and save the precipitation for a given hour
    """
    nc = lib.load_netcdf(ts)
    stations = lib.load_stations()

    # Okay, now we are going to step thru the hour
    ts0 = ts
    ts1 = ts + mx.DateTime.RelativeDateTime(hours=1)
    interval = mx.DateTime.RelativeDateTime(minutes=5)

    # Step 1: ________________________
    # Load up the reflectivities
    reflect = numpy.zeros((12, len(nc.dimensions['lat']), len(nc.dimensions['lon'])), 'f')
    i = -1
    now = ts0 + interval
    while now <= ts1:
        i += 1
        fp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png")
        if not os.path.isfile(fp):
            now += interval
            continue
        n0r = gdal.Open(fp, 0)
        n0rd = n0r.ReadAsArray() # 2600, 6000 --> row, col
        x0,y0 = lib.composite_lalo2pt(40.37, -96.64)
        x1,y1 = lib.composite_lalo2pt(43.50, -90.14)
        d = (numpy.flipud( n0rd[y1:y0,x0:x1] ) - 6.0) * 5.0 # to dBZ
        # Greater than 50 dbZ causes Z-R to freak
        d = numpy.where( d > 50, 50, d)
        reflect[i,:,:] = d
        del n0rd
        del n0r 

        now += interval
    total_reflect = numpy.sum( reflect, 0)
    max_reflect = numpy.max( reflect, 0)

    # Step 2: _____________ Create RH, precip mask
    #asos = pg.connect('asos', 'iemdb', user='nobody')
    #rs = asos.query("""SELECT station, max(tmpf) as t, max(dwpf) as d,
    #     max(CASE WHEN p01m > 0 THEN p01m ELSE 0 END) as mm from t%s WHERE
    #     valid > '%s+00' and valid <= '%s+00' and station in %s
    #     and tmpf > -50 and dwpf > -50 GROUP by station""" % (
    #     ts.year, ts0.strftime("%Y-%m-%d %H:%M"), 
    #     ts1.strftime("%Y-%m-%d %H:%M"), 
    #     str(tuple(stations.keys())) ) ).dictresult()
    #lats = []
    #lons = []
    #relh = []
    #p01m = []
    #for i in range(len(rs)):
    #    stid = rs[i]['station']
    #    if not stations.has_key(stid):
    #        continue
    #    lats.append( stations[stid]['lat'] )
    #    lons.append( stations[stid]['lon'] )
     #   relh.append( mesonet.relh( rs[i]['t'], rs[i]['d'] ) )
     #   p01m.append( rs[i]['mm'] )
#
    #rh = Ngl.natgrid(lons, lats, relh, nc.variables['lon'][:], 
    #     nc.variables['lat'][:])
    #pc = Ngl.natgrid(lons, lats, p01m, nc.variables['lon'][:], 
    #     nc.variables['lat'][:])

    # Print some diagnostics
    #print "Mean RH is %.2f" % (numpy.average(rh),)
    #print "Mean PC is %.2f" % (numpy.average(pc),)

    #print "Ob rain cells and < 70% humidity", numpy.sum( 
    #      numpy.where( pc > 1.0, numpy.where(rh < 70.0,1,0),  0) )

    # Now for our logic...
    # z = 300 r^1.4  mm/hr
    result = numpy.zeros((4, len(nc.dimensions['lat']), len(nc.dimensions['lon'])), 'f')
    raw_rates = numpy.power(numpy.power(10.0,(reflect/10.0)) / 200.0 , 1.0/1.6) / 12.0  # For a 5min period
    result[0,:,:] = numpy.sum( raw_rates[0:3,:,:], 0)
    result[1,:,:] = numpy.sum( raw_rates[3:6,:,:], 0)
    result[2,:,:] = numpy.sum( raw_rates[6:9,:,:], 0)
    result[3,:,:] = numpy.sum( raw_rates[9:12,:,:], 0)

    # Need to figure out the time index
    monstart = ts + mx.DateTime.RelativeDateTime(day=1,hour=0,minute=0)
    tdx0 = int( (ts-monstart).minutes / 15.0 )
    tdx1 = int( (ts1-monstart).minutes / 15.0 )

    print tdx0, tdx1, raw_rates[:,100,100], reflect[:,100,100],result[:,100,100]

    nc.variables['precipitation'][tdx0:tdx1,:,:] = result
    nc.close()
    del nc

#reflect = numpy.arange(-25,75,5)
#print numpy.power( numpy.power(10.0,reflect/10.0) / 300.0, 1.0/1.4)
sts = mx.DateTime.DateTime(1997,5,1,0,0)
ets = mx.DateTime.DateTime(1997,6,1,0,0)
interval = mx.DateTime.RelativeDateTime(hours=1)
now = sts
while now < ets:
  do(now)
  now += interval
