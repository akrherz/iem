import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import network
nt = network.Table("IACLIMATE")

ccursor.execute("""SELECT station, avg(sum) from (SELECT station, year, 
    sum(precip) from alldata_ia WHERE year > 1950 
    GROUP by station, year) as foo GROUP by station
    """)

lats = []
lons = []
vals = []
for row in ccursor:
    if not nt.sts.has_key(row[0]) or row[0][2] == 'C':
        continue
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )
    vals.append( row[1] * 25.4 )
    
cfg = {
       'wkColorMap': 'gsltod',
#       'wkColorMap': 'BlAqGrYeOrRe',
'_valid': '1951-2012',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_title'             : "Iowa Average Yearly Precipitation",
 'lbTitleString'      : "[mm] ", 
       
       }
import iemplot

fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp, None, fname='test.png')