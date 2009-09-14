# Yipppeee, this is what I worked so hard to get at, a climate file generator
# for WEPP from my fancy pant data...

import sys
sys.path.append("/mnt/a2/wepp/iemcligen/")
import pg, mx.DateTime, netCDF3, lib, editclifile, cliRecord, numpy
# Connect to the WEPP database
mydb = pg.connect('wepp', 'iemdb', user='nobody')

# Figure out for which month we are interested in...
monthts = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), 1)

# Open up our NetCDF datafile!
nc = lib.load_netcdf( monthts )

# Load up our climate observations
climatedata = [0]*32
sts = monthts
ets = monthts + mx.DateTime.RelativeDateTime(months=1)
now = sts
idx = ['0', 'NW', 'NC', 'NE', 'WC', 'C', 'EC', 'SW', 'SC', 'SE']
while now < ets:
  data = {}
  for i in range(1,10):
      data[ idx[i] ] = mydb.query("SELECT * from climate_sectors WHERE \
                     sector = %s and day = '%s'" \
                     % (i, now.strftime("%Y-%m-%d") ) ).dictresult()
  climatedata[now.day] = data
  now += mx.DateTime.RelativeDateTime(days=1)

times = [0]*96
times[0] = "00.14"
for i in range(1,96):
    myts = monthts + mx.DateTime.RelativeDateTime(seconds=+ i*900)
    hr = myts.strftime("%H")
    mi = int(myts.strftime("%M"))
    frac = mi / 60.0
    times[i] = "%s.%02i" % (hr, frac * 100)
times[95] = "23.90"



def doBreakPoint(lat, lon, day):
    """
    Actually compute the breakpoint data, hmmm
    """
    x,y = lib.nc_lalo2pt(nc, lat, lon)
    t0 = (day - 1) * 96 + 24  # 6 hours tz offset
    t1 = day * 96       + 24  # 6 hours tz offset
    if t1 > numpy.shape(nc.variables['precipitation'])[0]:
        t1 = numpy.shape(nc.variables['precipitation'])[0]
    data15 = nc.variables['precipitation'][t0:t1,y,x]
    threshold = 0.1 * 25.4  # Threshold is 2/10 of an inch
    accum = 0.00
    writeAccum = 0.00
    lastTime = 0
    lines = 0
    bkTxt = ""
    cliFrmt = "%-12s%-12.3f\n"

    rAccum = 0  # Running Accumulation
    tAccum = 0  # Total Accumulation
    cnt = 0
    for accum in data15:
        rAccum += accum
        tAccum += accum
        if rAccum > threshold:
             bkTxt += cliFrmt % (times[cnt], tAccum)
             rAccum = 0
        cnt += 1                                                            
    if rAccum > 0:
        bkTxt += cliFrmt % (times[cnt-1], tAccum)

    if tAccum < (0.05 * 25.4): # Minimum Threshold
        bkTxt = ""
    return bkTxt


# Figure out which HRAP cells we care about
rs = mydb.query("""
SELECT mgtzone, hrap_i, 
 x(transform(centroid(the_geom),4326)) as lon, 
 y(transform(centroid(the_geom),4326)) as lat
from hrap_polygons WHERE used = 't'
""").dictresult()
for i in range(len(rs)):
    if i % 100 == 0:
        print 'Processed %s entries' % (i,)
    hrap_i = int(rs[i]['hrap_i'])
    mgtzone = rs[i]['mgtzone']
    lat = rs[i]['lat']
    lon = rs[i]['lon']

    cf = editclifile.editclifile('clifiles/%s.dat' % (hrap_i,) )
    sts = monthts
    ets = monthts + mx.DateTime.RelativeDateTime(months=1)
    now = sts
    while now < ets:
        cr = cliRecord.cliRecord(now)
        bktxt = doBreakPoint(lat, lon, now.day)
        cr.BPset(bktxt)
        cr.CLset(climatedata[now.day][mgtzone][0])
        cf.editDay(now, cr)
        now += mx.DateTime.RelativeDateTime(days=1)
    cf.write()
    del cf
