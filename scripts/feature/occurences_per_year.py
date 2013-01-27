"""
Number of 100 degree days per year 
"""
import network
nt  = network.Table("IACLIMATE")
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

lats = []
lons = []
vals = []

for sid in nt.sts.keys():
    if sid[2] == 'C' or sid == 'IA0000':
        continue
    ccursor.execute("""
  select year, avg((high+Low)/2.0) from alldata_ia where 
  station = %s and sday < '1213' GROUP by year ORDER by avg DESC
    """, (sid,))
    rank = 1
    for row in ccursor:
        if row[0] == 2012:
            break
        rank += 1

    lats.append( nt.sts[sid]['lat'] )    
    lons.append( nt.sts[sid]['lon'] )
    vals.append( rank )
    
import iemplot

cfg = {
       '_title': 'Year to Date Average Temperature Rank',
       '_valid': '12 Dec 2012, #1 would be warmest on record',
       '_showvalues': True,
       '_format': '%.0f',
       'lbTitleString': 'Days/Yr'
       }

tmpfp = iemplot.simple_valplot(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)
