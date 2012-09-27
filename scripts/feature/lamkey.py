import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import network
nt = network.Table("IACLIMATE")

ccursor.execute("""
--- select station, avg(sum) from (select station, year, sum(precip) from alldata_ia where station in (select distinct station from alldata_ia where year = 1931 and precip > 0) and year between 1981 and 2010 GROUP by station, year) as foo GROUP by station

select station, sum(precip) from climate71 GROUP by station
""")
previous = {}
for row in ccursor:
    previous[row[0]] = row[1]

ccursor.execute("""
select station, avg(sum) from (select station, year, sum(precip) from alldata_ia where station in (select distinct station from alldata_ia where year = 1931 and precip > 0) and year between 1931 and 1960 GROUP by station, year) as foo GROUP by station
""")

lats = []
lons = []
vals = []

for row in ccursor:
    if not nt.sts.has_key(row[0]):
        continue
    vals.append( previous[row[0]]  )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )
    
import iemplot

cfg = {
       '_title': '1981-2010  Yearly Average Precipitation',
       'lbTitleString': 'in',
       '_showvalues': True,
       '_format': '%.2f',
       }

tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)