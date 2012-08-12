
import mesonet, iemdb
import iemplot
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import network
nt = network.Table(("IACLIMATE", "MNCLIMATE", "NDCLIMATE", "SDCLIMATE",
 "NECLIMATE", "KSCLIMATE", "MOCLIMATE", "KYCLIMATE", "ILCLIMATE", "WICLIMATE",
 "INCLIMATE", "OHCLIMATE", "MICLIMATE"))

import mx.DateTime

ccursor.execute("""select obs.station, obs.avg, climate.avg, obs.avg - climate.avg as d 
  from (select avg((high+low)/2.0), station from alldata where month = 7 
  and year = 2012 GROUP by station) as obs, (SELECT station, avg((high+low)/2.0) 
  from climate WHERE extract(month from valid) = 7 GROUP by station) as climate 
  WHERE climate.station = obs.station ORDER by d DESC""")
vals = []
lats = []
lons = []

for row in ccursor:
    if not nt.sts.has_key(row[0]):
        continue
    #if row[0][:4] == '0000' or row[0][2] == 'C':
    if row[0][2] != 'C':
        continue
    vals.append( row[3] )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )
    

cfg= {'lbTitleString': '[F]',
      '_midwest': True,
      'cnLevelSelectionMode': 'ManualLevels',
      'cnLevelSpacingF'      : 1.0,
    'cnMinLevelValF'       : -8.0,
    'cnMaxLevelValF'       : 8.0,
    '_showvalues': True,
    '_format': '%.1f',

      }

tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)
