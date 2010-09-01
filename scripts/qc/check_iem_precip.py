"""
Need something to daily QC the schoolnet precipitation against iemre I guess
"""
import iemdb
import psycopg2.extras
import sys
sys.path.insert(0, "../iemre")
import constants
import netCDF3
import mx.DateTime
import numpy
ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1,hour=0,minute=0,second=0)


# Load up netcdf file
nc = netCDF3.Dataset("/mnt/mesonet/data/iemre/%s_daily.nc" % (ts.year,),'r')
p01d = nc.variables['p01d']
offset = int((ts - (ts + mx.DateTime.RelativeDateTime(month=1,day=1))).days)


iem = iemdb.connect("iem", bypass=True)
icursor = iem.cursor(cursor_factory=psycopg2.extras.DictCursor)
icursor.execute("""SELECT x(geom) as lon, y(geom) as lat, station, pday
  FROM summary where network in ('KCCI','KIMT','AWOS') and day = 'YESTERDAY'::date
  ORDER by pday DESC""")
obs = []
estimates = []
fmt = "%7s %5s OB: %.2f EST: %4.2f"
for row in icursor:
    station = row['station']
    lat = row['lat']
    lon = row['lon']
    # Lookup IEMRE data
    ix,jy = constants.find_ij(lon, lat)
    estimate = p01d[offset,jy,ix] / 25.4
    # If site is offline, we could care less
    if row['pday'] < 0:
        continue
    elif row['pday'] < 0.1 and estimate < 0.1:
        continue
    elif row['pday'] < 0.1 and estimate > 0.25:
        print fmt % ('UNDER', station, row['pday'], estimate)
    elif row['pday'] > 0.25 and estimate < 0.1:
        print fmt % ('OVER', station, row['pday'], estimate)
    elif (row['pday'] - estimate) > (0.5 * estimate):
        print  fmt % ('50OVER', station, row['pday'], estimate)
    elif (estimate - row['pday']) > (0.5 * estimate):
        print fmt % ('50UNDER', station, row['pday'], estimate)

    obs.append( row['pday'] )
    estimates.append( estimate )

obs = numpy.array( obs )
estimates = numpy.array( estimates )
print 'OBS BIAS %.2f (%.2f%%) RMSE: %.2f' % (numpy.average( obs - estimates),
   numpy.average( obs - estimates) / numpy.average( estimates ) * 100.0,
   numpy.average(( obs - estimates ) * (obs - estimates))**.5 )
