# Month percentile 
import iemdb, network
import iemplot
nt = network.Table("IACLIMATE")
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()
ccursor.execute("""
 select foo2.station, max(foo2.min) as maxprev, min(foo.d2012) as thisyear, 
 sum(case when foo.d2012 > foo2.min then 1 else 0 end), count(*) from 

   (select station, extract(year from day + '0 months'::interval) as yr, 
   avg((high+low)/2.0) as min from alldata_ia where month in (6,7,8)  
   GROUP by station, yr) as foo2, 

   (select station, avg((high+low)/2.0) as d2012 from alldata_ia where month in (6,7,8) 
   and station != 'IA0000' and substring(station,2,1) != 'C'
   and year = 2012 GROUP  by station) as foo 

 where foo.station = foo2.station GROUP by foo2.station
""")
lats = []
lons = []
vals = []
for row in ccursor:
    print row
    if not nt.sts.has_key(row[0]):
        continue
    vals.append( float(row[3]) / float(row[4]) * 100.0 )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "2012 Summer Average Temperature Percentile",
 '_valid'             : "1 Jun 2012 - 31 Aug 2012, comparing 1893-2011 [100% Warmest]",
 'lbTitleString'      : "[%]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)