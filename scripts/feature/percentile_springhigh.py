# Month percentile 
import iemdb, network
import iemplot
nt = network.Table("IACLIMATE")
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()
ccursor.execute("""
 select foo2.station, max(foo2.min) as maxprev, min(foo.d2012) as thisyear, 
 sum(case when foo.d2012 > foo2.min then 1 else 0 end), count(*) from 

   (select station, extract(year from day + '3 months'::interval) as yr, 
   min(low) from alldata_ia where month in (10,11,12,1)  
   and day < '2011-09-01' and (sday > '0901' or sday < '0111') and station = 'IA2203'
   GROUP by station, yr) as foo2, 

   (select station, min(low) as d2012 from alldata_ia where day > '2011-09-01' 
   GROUP  by station) as foo 

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
 '_title'             : "2011-2012 Coldest Winter Temperature Percentile",
 '_valid'             : "1 Nov 2011 - 9 Jan 2012, comparing 1893-2010 [100% Warmest]",
 'lbTitleString'      : "[%]",
 '_showvalues'        : True,
 '_format'            : '%.0f',
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)