# Compute the composite timeseries, hmmmm

import numpy, mx.DateTime, sys
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

# Lets first query the database for events
rs = postgis.query("""SELECT distinct wfo, eventid, significance, phenomena,
     issue, expire from sbw_2008 WHERE phenomena = 'TO'""").dictresult()
# Create data array
data = numpy.zeros( (len(rs),90), numpy.float )

# Loop over
for i in range(len(rs)):
  # Go find the series of warnings now
  sts = mx.DateTime.strptime(rs[i]['issue'][:16], '%Y-%m-%d %H:%M')
  ets = mx.DateTime.strptime(rs[i]['expire'][:16], '%Y-%m-%d %H:%M')
  try:
    rs2 = postgis.query("""SELECT polygon_begin, polygon_end, 
        area( transform(geom,2163)) as area from sbw_2008 WHERE
        wfo = '%s' and phenomena = '%s' and eventid = %s and significance
        = '%s' ORDER by polygon_begin ASC""" % (rs[i]['wfo'], 
        rs[i]['phenomena'], rs[i]['eventid'], 
        rs[i]['significance'])).dictresult()
  except:
    print rs[i]
    sys.exit()
  initialsz = rs2[0]['area']
  for j in range(len(rs2)):
    psts = mx.DateTime.strptime(rs2[j]['polygon_begin'][:16], '%Y-%m-%d %H:%M')
    pets = mx.DateTime.strptime(rs2[j]['polygon_end'][:16], '%Y-%m-%d %H:%M')
    psz = rs2[j]['area']
    tix = (psts - sts).minutes
    tox = (pets - sts).minutes
    data[i, tix:tox ] = psz / initialsz

  #data[i, tox:90 ] = psz / initialsz

final = numpy.ma.masked_values(data,0)
print final[1,:]
print data[1,:]
#print mask[1,:]

for min in range(90):
  print "%s,%.3f" % (min, numpy.ma.average(final[:,min]))
