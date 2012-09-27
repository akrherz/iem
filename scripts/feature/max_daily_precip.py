import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import network
nt = network.Table("IACLIMATE")

ccursor.execute("""
 SELECT one.station, max(one.precip + two.precip) from 
 (SELECT station, day as d1, precip from alldata_ia where year = 2012 
 and day >= '2012-05-01') as one, 
 (SELECT station, day + '1 day'::interval as d2, precip from alldata_ia where year = 2012 
 and day >= '2012-05-01') as two WHERE one.station = two.station
 and one.d1 = two.d2 GROUP by one.station
 
""")

lats = []
lons = []
vals = []
for row in ccursor:
    if row[0][2] == 'C' or row[0][2:] == '0000':
        continue
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )
    vals.append( row[1] )
    
cfg = {'lbTitleString': 'inch',
       '_title': "Max"
       
       }

import iemplot
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)