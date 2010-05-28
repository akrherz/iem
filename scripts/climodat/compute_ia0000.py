# Compute the stats for the ia0000 site, Iowa's Average Site

import numpy, Ngl, sys
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

def doday(now):
  """
  Do the estimation for a given date!
  """
  data = {}
  for var in ['high','low','precip','snow']:
    data[var] = do(now, var)
  print "%s HIGH: %.1f LOW: %.1f PRECIP: %.2f SNOW: %.2f" % (
    now.strftime("%Y-%m-%d"), data["high"], data["low"], data["precip"],
    data["snow"])
  coop.query("DELETE from alldata WHERE stationid = 'ia0000' and day = '%s'" % ( now.strftime("%Y-%m-%d"),))
  sql = """INSERT into alldata 
    (stationid, day, high, low, precip, snow, snowd, estimated, year, month, 
    sday, climoweek)
    VALUES ('ia0000', '%s', %.0f, %.0f, %.2f, %.1f, 0, true, %s, %s, '%s', 
    (select climoweek from climoweek where sday = '%s'))""" % (
    now.strftime("%Y-%m-%d"), data['high'], data['low'], data['precip'], 
    data['snow'], now.year, now.month, now.strftime("%m%d"), 
     now.strftime("%m%d"))
  coop.query(sql)

if len(sys.argv) == 4:
  now = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), 
     int(sys.argv[3]))
  doday(now)
elif len(sys.argv) == 3:
  sts = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), 1 )
  ets = sts + mx.DateTime.RelativeDateTime(months=1)
  interval = mx.DateTime.RelativeDateTime(days=1)
  now = sts
  while now < ets:
    doday(now)
    now += interval
else:
  now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
  doday(now)
