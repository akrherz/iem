# Month percentile 
import iemdb, network
import iemplot
nt = network.Table("IACLIMATE")
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()
ccursor.execute("""
 ---select foo2.station, max(foo2.min) as maxprev, min(foo.d2013) as thisyear, 
 ---sum(case when foo.d2013> foo2.min then 1 else 0 end), count(*) from 
---
 ---  (select station, extract(year from day + '0 months'::interval) as yr, 
 ---  avg((high+low)/2.0) as min from alldata_ia where sday < '0327' 
 ---  GROUP by station, yr) as foo2, 
---
---   (select station, avg((high+low)/2.0) as d2013 from alldata_ia 
---   where sday < '0327' 
---   and station != 'IA0000' and substring(station,2,1) != 'C'
---   and year = 2013 GROUP  by station) as foo 

--- where foo.station = foo2.station GROUP by foo2.station
 SELECT station, max(high) from alldata_ia where year = 2013 and
 station != 'IA0000' and substring(station,2,1) != 'C' GROUP by station
""")
lats = []
lons = []
vals = []
for row in ccursor:
    print row
    if not nt.sts.has_key(row[0]):
        continue
    #vals.append( float(row[3]) / float(row[4]) * 100.0 )
    vals.append( row[1] )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2013 Maximum Temperature",
 '_valid'             : "1 Jan 2013 - 27 Mar 2013",
 'lbTitleString'      : "[F]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)