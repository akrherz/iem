"""
Number of 100 degree days per year 
"""
import network
nt  = network.Table("IACLIMATE")
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
  select station, max(year) from alldata_ia
  where station != 'IA0000' and 
  station != 'IA7979' and substr(station,2,1) != 'C'
  and high > 99 GROUP by station
""")

lats = []
lons = []
vals = []
for row in ccursor:
    if not nt.sts.has_key(row[0]):
        continue
    lats.append( nt.sts[row[0]]['lat'] )    
    lons.append( nt.sts[row[0]]['lon'] )
    vals.append( row[1] )
    
import iemplot

cfg = {
       '_title': 'Year of last 100 degree Temperature',
       '_valid': 'based on long term Iowa Climate sites',
       '_showvalues': True,
       '_format': '%.0f',
       'lbTitleString': 'Days/Yr'
       }

tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)
