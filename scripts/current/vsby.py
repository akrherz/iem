"""
 Generate current plot of visibility
"""

import sys
import os
import iemplot
import random

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
SELECT 
  id, network, vsby, x(geom) as lon, y(geom) as lat
FROM 
  current c JOIN stations s ON (s.iemid = c.iemid)
WHERE
  s.network IN ('AWOS', 'IA_ASOS','IL_ASOS','MN_ASOS','WI_ASOS','SD_ASOS',
              'NE_ASOS','MO_ASOS') and
  valid + '15 minutes'::interval > now() and
  vsby >= 0 and vsby <= 10
"""

lats = []
lons = []
vals = []
valmask = []
icursor.execute(sql)
for row in icursor:
    lats.append( row[4] )
    lons.append( row[3] )
    vals.append( row[2] )
    valmask.append( row[1] in ['AWOS','IA_AWOS'] )

if len(lats) < 5:
    sys.exit(0)

cfg = {
 'wkColorMap': 'gsdtol',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa Visibility",
 '_valid'             : now.strftime("%d %b %Y %-I:%M %p"),
 '_showvalues'        : True,
 '_format'            : '%.1f',
 '_valuemask'         : valmask,
 'lbTitleString'      : "[miles]",
 'cnLevelSelectionMode': "ExplicitLevels",
 'cnLevels' : [0.01,0.1,0.25,0.5,1,2,3,5,8,9.9],
 'lbLabelStrings' : [0.01,0.1,0.25,0.5,1,2,3,5,8,10],
 'cnExplicitLabelBarLabelsOn': True,
}
# Generates tmp.ps
#print "Max visibility %.3f Min Visibility: %.3f" % (max(vals), min(vals))
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

pqstr = "plot ac %s00 iowa_vsby.png vsby_contour_%s00.png png" % ( 
   mx.DateTime.gmt().strftime("%Y%m%d%H"), mx.DateTime.gmt().strftime("%H") )
iemplot.postprocess(tmpfp, pqstr)
