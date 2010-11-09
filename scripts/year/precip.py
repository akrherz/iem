import sys
import iemplot

import Ngl
import numpy
import re, os
import math
import mx.DateTime
import netCDF3
import iemdb, network
st = network.Table('IACLIMATE')
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

nrain = []
lats = []
lons = []

# Get normals!
ccursor.execute("""SELECT station, sum(precip) as acc from climate51 
    WHERE valid <= '2000-%s' and station NOT IN ('ia7842','ia4381') 
    GROUP by station ORDER by acc ASC""" % (ts.strftime("%m-%d"),
    ) )
for row in ccursor:
    station = row[0].upper()
    #print station, rs[i]['acc']
    nrain.append( row[1] )
    lats.append(st.sts[station]['lat'])
    lons.append(st.sts[station]['lon'])


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_title'             : "Iowa %s Normal Precipitation Accumulation" % (
                        ts.strftime("%Y"), ),
 '_valid'          : "1 Jan - %s" % (
                        ts.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[inch] ",
}
tmpfp = iemplot.simple_contour(lons, lats, nrain, cfg)
pqstr = "plot c 000000000000 summary/year/normals.png bogus png"
iemplot.postprocess(tmpfp, pqstr)

# ----------------------------------
# - Compute departures
drain = []
lats = []
lons = []
ccursor.execute("""select station, norm, obs from 
    (select c.station, sum(c.precip) as norm from climate51 c 
     where c.valid < '2000-%s' GROUP by c.station) as climate, 
    (select a.stationid, sum(a.precip) as obs from alldata a 
     WHERE a.year = %s GROUP by stationid) as obs 
  WHERE obs.stationid = climate.station""" % (ts.strftime("%m-%d"),
    ts.year) )
for row in ccursor:
    station = row[0].upper()
    #print station, rs[i]['acc']
    drain.append( row[2] - row[1] )
    lats.append(st.sts[station]['lat'])
    lons.append(st.sts[station]['lon'])


cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_title'             : "Iowa %s Precipitation Departure" % (
                        ts.strftime("%Y"), ),
 '_valid'          : "1 Jan - %s" % (
                        ts.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[inch] ",
}
tmpfp = iemplot.simple_contour(lons, lats, drain, cfg)
pqstr = "plot c 000000000000 summary/year/diff.png bogus png"
iemplot.postprocess(tmpfp, pqstr)

# -----------------------------------
# - Stage4 Observations
nc = netCDF3.Dataset("/mnt/a2/wepp/data/rainfall/netcdf/yearly/%srain.nc" % (ts.year,) )
ncrain = nc.variables["yrrain"][:] 
lats = nc.variables["latitude"][:]
lons = nc.variables["longitude"][:]

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_title'             : "Iowa %s Precipitation Accumulation" % (
                        ts.strftime("%Y"), ),
 '_valid'          : "1 Jan - %s" % (
                        ts.strftime("%d %b %Y"), ),
 'lbTitleString'      : "[inch] ",
}
tmpfp = iemplot.simple_grid_fill(lons, lats, ncrain, cfg)
pqstr = "plot c 000000000000 summary/year/stage4obs.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
 



