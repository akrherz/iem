from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']

import numpy
from scipy import stats
import netCDF3
import mx.DateTime

sts = mx.DateTime.DateTime(1900,2,1)
ets = mx.DateTime.DateTime(2010,7,12)

nc = netCDF3.Dataset('autocor.nc', 'w')
nc.createDimension('day', int((ets - sts).days) +1)

vals = nc.createVariable('rval', numpy.float, ('day',) )
precip = nc.createVariable('precip', numpy.float, ('day',) )

day = nc.createVariable('day', numpy.double, ('day',) )
day.units = 'days since 1900-02-01'
day[:] = range( int((ets - sts).days) +1)

rs = coop.query("""SELECT high, precip from alldata WHERE stationid = 'ia0000'
     and day >= '1900-01-01' ORDER by day ASC""").dictresult()
highs = numpy.zeros( int((ets - sts).days) + 32 )
p = numpy.zeros( int((ets - sts).days) + 32 )
for i in range(len(rs)):
  highs[i] = rs[i]['high']
  p[i] = rs[i]['precip']

for i in range(31,len(highs)):
  slope, intercept, r_value, p_value, std_err = stats.linregress(
      highs[i-31:i-1],highs[i-30:i])
  vals[i-31] = r_value
  precip[i-31] = numpy.sum( p[i-30:i] )
  if numpy.sum( p[i-30:i] ) > 10:
    print numpy.sum( p[i-30:i] ), (sts + mx.DateTime.RelativeDateTime(days=(i-30))), (sts + mx.DateTime.RelativeDateTime(days=(i-61)))

nc.close()

# Statewide
# 10.32 2010-06-23
# 10.35 2008-06-23
# 12.26 1993-07-29
# 10.19 1926-09-29
