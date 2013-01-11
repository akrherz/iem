import iemdb, mesonet
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import network
nt = network.Table("IACLIMATE")

ccursor.execute("""SELECT station, avg((high+low)/2.0) from alldata_ia
 WHERE year > 1950 GROUP by station""")

lats = []
lons = []
vals = []
for row in ccursor:
    if not nt.sts.has_key(row[0]) or row[0][2] == 'C':
        continue
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )
    vals.append( float(row[1])  )
    
cfg = {
       'wkColorMap': 'BlAqGrYeOrRe',
       'wkColorMap': 'gsltod',
       '_valid': '1950-2012',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_title'             : "Iowa Average Temperature",
 'lbTitleString'      : "[C] ", 
       
       }
import iemplot

fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp, None, fname='test.png')