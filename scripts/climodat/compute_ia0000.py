# Compute the stats for the ia0000 site, Iowa's Average Site

import numpy, Ngl
import mx.DateTime
from pyIEM import iemdb, stationTable
i = iemdb.iemdb()
coop = i['coop']
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")

numxout = 20
numyout = 20
xmin    = -96.6
ymin    = 40.0
xmax    = -90.1
ymax    = 43.5

xc      = (xmax-xmin)/(numxout-1)
yc      = (ymax-ymin)/(numyout-1)

xo = xmin + xc*numpy.arange(0,numxout)
yo = ymin + yc*numpy.arange(0,numyout)


def do(now, var):
  # Create Grid
  lats = []
  lons = []
  vals = []
  # Extract Data
  sql = "SELECT %s, upper(stationid) as s from alldata WHERE day = '%s' and \
         %s is NOT NULL" % (var, now.strftime("%Y-%m-%d"), var)
  rs = coop.query(sql).dictresult()
  for i in range(len(rs)):
    if not st.sts.has_key(rs[i]['s']):
      continue
    lats.append( st.sts[ rs[i]['s'] ]['lat'] )
    lons.append( st.sts[ rs[i]['s'] ]['lon'] )
    vals.append( float(rs[i][var]) )
  # Grid Var
  g = Ngl.natgrid(lons, lats, vals, xo, yo)
  # Return mean of grid
  return numpy.average(g)


now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
data = {}
for var in ['high','low','precip','snow']:
  data[var] = do(now, var)
print now, data
sql = "INSERT into alldata \
(stationid, day, high, low, precip, snow, snowd, estimated, year, month, sday)\
 VALUES ('ia0000', '%s', %.0f, %.0f, %.2f, %.1f, 0, true, %s, %s, '%s')" \
% (now.strftime("%Y-%m-%d"), data['high'], data['low'], data['precip'], \
data['snow'], now.year, now.month, now.strftime("%m%d"))
coop.query(sql)
