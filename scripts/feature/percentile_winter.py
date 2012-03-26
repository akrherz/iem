# Month percentile 

import sys, os, random
sys.path.append("../lib/")
import iemplot
import network
nt = network.Table("IACLIMATE")

import mx.DateTime
now = mx.DateTime.now()
import pg
coop = pg.connect('coop','iemdb',user='nobody')

# Extract normals
lats = []
lons = []
vals = []
rs = coop.query("""SELECT station, avg((high+low)/2.0) as rain from alldata_ia
     WHERE 
     station not in ('IA0000','IA5230') and substr(station,3,1) != 'C' and day > '2011-11-30' GROUP by station ORDER by station ASC""").dictresult()
for i in range(len(rs)):
  stid = rs[i]['station']
  if not nt.sts.has_key( rs[i]['station'].upper() ):
    continue
  lats.append( nt.sts[ rs[i]['station'].upper() ]['lat'] )
  lons.append( nt.sts[ rs[i]['station'].upper() ]['lon'] )
  obs = rs[i]['rain'] 
  # Find obs
  rs2 = coop.query("""SELECT 
        extract(year from day + '1 month'::interval) as yr, 
        avg((high+low)/2.0) as rain from alldata_ia where
        station = '%s' and month in (12,1,2) GROUP by yr ORDER by rain ASC
        """ % (stid,) ).dictresult()
  for j in range(len(rs2)):
    if rs2[j]['rain'] >= obs:
      break
  vals.append( (j+1) / float(len(rs2)) * 100.0 )
  print rs2[j]['rain'], obs, rs[i]['station'], (j+1) / float(len(rs2)) * 100.0 

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa Average Winter Temperature Percentile",
 '_valid'             : "1 Dec 2011 - 29 Feb 2012 (100 warmest)",
 'lbTitleString'      : "[%]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(tmpfp, "")
iemplot.makefeature(tmpfp)
