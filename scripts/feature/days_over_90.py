# Compute the number of days over 90 this year, please

import mx.DateTime
import iemdb, iemplot
IEM = iemdb.connect("iem", bypass=True)
COOP = iemdb.connect('coop', bypass=True)
icursor = IEM.cursor()
ccursor = COOP.cursor()

icursor.execute("""
SELECT station, obs, d90, climate_site, lon, lat
FROM
 (SELECT station,  
 sum( case when max_tmpf > -50 then 1 else 0 end) as obs,
 sum( case when max_tmpf >= 90 then 1 else 0 end) as d90 from summary_2010
 WHERE network in ('IA_ASOS','AWOS') and x(geom) between -120 and -60
 GROUP by station) as foo,
 (SELECT id, x(geom) as lon, y(geom) as lat, climate_site from stations) as s
 WHERE s.id = foo.station
""")
lats = []
lons = []
vals = []
for row in icursor:
    if row[1] < 263:
        continue
    lats.append( row[5] )
    lons.append( row[4] )
    ob = row[2]
    ccursor.execute("""
    select avg(cnt) from (SELECT year, count(*) as cnt from alldata where stationid = %s and high >= 90
    GROUP by year) as foo
    """, (row[3].lower(),))
  
    climate = ccursor.fetchone()[0]
    vals.append(ob)
    
cfg = {
        'wkColorMap': 'BlAqGrYeOrRe',
        'nglSpreadColorStart': 2,
        'nglSpreadColorEnd'  : -1,
        '_showvalues'   : True,
        '_format'       : '%.0f',
           '_title'             : "2010 Days over 90",
        '_valid'             : mx.DateTime.now().strftime("%d %b %Y"),
 'lbTitleString'      : "days",

       }

fp = iemplot.simple_contour(lons,lats,vals,cfg)
iemplot.postprocess(fp,"","")