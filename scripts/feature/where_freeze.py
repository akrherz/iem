# 

import sys, os
sys.path.append("../lib/")
import iemplot

import mx.DateTime
now = mx.DateTime.now()

from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
mesosite = i['mesosite']
#entries = {}
#for year in range(1951,2009):
#  rs = coop.query("""
#  SELECT stationid from alldata WHERE day = 
#  (SELECT min(day) from alldata WHERE year = %s and month > 8 and low < 32) 
#  and stationid IN
#  (SELECT distinct stationid from alldata WHERE year = 1951)
#  and low < 32""" % (year,)).dictresult()
#  for i in range(len(rs)):
#    station = rs[i]['stationid']
#    if not entries.has_key(station):
#      entries[station] = 0
#    entries[station] += 1
#print entries
entries = {'ia7726': 13, 'ia0112': 1, 'ia2977': 5, 'ia5837': 1, 'ia8806': 8, 'ia0200': 2, 'ia6327': 2, 'ia7842': 15, 'ia7844': 10, 'ia1962': 1, 'ia7312': 4, 'ia5123': 9, 'ia8296': 3, 'ia8755': 2, 'ia4049': 6, 'ia1277': 3, 'ia4228': 2, 'ia0213': 5, 'ia4502': 1, 'ia5230': 5, 'ia5235': 12, 'ia3718': 10, 'ia5131': 2, 'ia0364': 15, 'ia6800': 6, 'ia7979': 4, 'ia3980': 4, 'ia0133': 4, 'ia4038': 5, 'ia6200': 7, 'ia3487': 4, 'ia8339': 5, 'ia2724': 8, 'ia2864': 12, 'ia2689': 1, 'ia7613': 2, 'ia3438': 1, 'ia5769': 1, 'ia5493': 4, 'ia9132': 3, 'ia4735': 9, 'ia6940': 3, 'ia3632': 1, 'ia2999': 3, 'ia5952': 5, 'ia5086': 5, 'ia6103': 5, 'ia3584': 4, 'ia2110': 7, 'ia0157': 2, 'ia3509': 7, 'ia7594': 15, 'ia8568': 4, 'ia1233': 12, 'ia1442': 11, 'ia1402': 5, 'ia0149': 1, 'ia1833': 2, 'ia4894': 2, 'ia0923': 6, 'ia1394': 4, 'ia4142': 4, 'ia6566': 3, 'ia3290': 2, 'ia8706': 8, 'ia7161': 2, 'ia0241': 1, 'ia1533': 3, 'ia6316': 2, 'ia7664': 16, 'ia7708': 5, 'ia0385': 10, 'ia6243': 5, 'ia7669': 1, 'ia2171': 2, 'ia2573': 2, 'ia4063': 2, 'ia4389': 1, 'ia1541': 7, 'ia1257': 4, 'ia6151': 6, 'ia3473': 6, 'ia6305': 1, 'ia5198': 1, 'ia1954': 7, 'ia7147': 11, 'ia0807': 5, 'ia6719': 6, 'ia0576': 1}
#entries = {'ia0133': 14, 'ia3584': 10, 'ia8806': 19, 'ia2110': 23, 'ia0200': 5, 'ia6327': 4, 'ia2203': 1, 'ia6243': 11, 'ia3509': 16, 'ia2171': 11, 'ia1319': 1, 'ia4063': 4, 'ia4389': 4, 'ia4381': 1, 'ia7147': 35, 'ia1833': 8, 'ia4894': 10, 'ia2864': 27, 'ia3473': 10, 'ia5769': 6, 'ia3290': 9, 'ia5198': 7, 'ia5230': 19, 'ia4735': 27, 'ia8706': 13, 'ia7161': 7, 'ia8266': 1, 'ia7979': 11, 'ia5131': 6, 'ia8688': 2, 'ia5952': 17, 'ia1533': 7, 'ia0364': 31, 'ia0000': 3}
#entries = {'ia7726': 13, 'ia0112': 1, 'ia2977': 5, 'ia5837': 1, 'ia8806': 19, 'ia0200': 5, 'ia5230': 19, 'ia7842': 32, 'ia7844': 10, 'ia1962': 1, 'ia5200': 2, 'ia7312': 4, 'ia5123': 9, 'ia6766': 1, 'ia8296': 3, 'ia4963': 1, 'ia8755': 2, 'ia1402': 5, 'ia8693': 3, 'ia1277': 3, 'ia4228': 2, 'ia0213': 5, 'ia4502': 1, 'ia6327': 4, 'ia5235': 12, 'ia3718': 10, 'ia5131': 6, 'ia0364': 31, 'ia6800': 6, 'ia0197': 1, 'ia7979': 11, 'ia3980': 4, 'ia0133': 14, 'ia4038': 5, 'ia6200': 7, 'ia2203': 1, 'ia2723': 3, 'ia3487': 4, 'ia8339': 5, 'ia2724': 8, 'ia2864': 27, 'ia2689': 1, 'ia7613': 2, 'ia3438': 1, 'ia5769': 6, 'ia5493': 4, 'ia9132': 3, 'ia7594': 15, 'ia6940': 3, 'ia3632': 1, 'ia2999': 3, 'ia8026': 2, 'ia5952': 17, 'ia7892': 2, 'ia5086': 5, 'ia6103': 5, 'ia3584': 10, 'ia2603': 3, 'ia2110': 23, 'ia0157': 2, 'ia3509': 16, 'ia4735': 27, 'ia8568': 4, 'ia1233': 12, 'ia1442': 11, 'ia4049': 6, 'ia0149': 1, 'ia1833': 8, 'ia4894': 10, 'ia0923': 6, 'ia1394': 4, 'ia4142': 4, 'ia6566': 3, 'ia3290': 9, 'ia8706': 13, 'ia7161': 7, 'ia8266': 1, 'ia0241': 1, 'ia1533': 7, 'ia0000': 3, 'ia0003': 1, 'ia6316': 2, 'ia7664': 16, 'ia7708': 5, 'ia0385': 10, 'ia6243': 11, 'ia7669': 1, 'ia7700': 3, 'ia2171': 11, 'ia1314': 1, 'ia2573': 2, 'ia1319': 1, 'ia4063': 4, 'ia4389': 4, 'ia1541': 7, 'ia1257': 4, 'ia4381': 1, 'ia6151': 6, 'ia3473': 10, 'ia6305': 1, 'ia5198': 7, 'ia1954': 7, 'ia7147': 35, 'ia4874': 2, 'ia8688': 2, 'ia0807': 5, 'ia6719': 6, 'ia0576': 1}

vals = []
lats = []
lons = []
rs = mesosite.query("SELECT id, x(geom) as lon, y(geom) as lat from stations WHERE network = 'IACLIMATE'").dictresult()
for i in range(len(rs)):
  id = rs[i]['id'].lower()
  if not entries.has_key(id):
    continue
  vals.append( entries[id] )
  lats.append( rs[i]['lat'] )
  lons.append( rs[i]['lon'] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_title'             : "Number of Years the Site recorded First Freeze [ties shared]",
 '_valid'             : "[1951-2008] based on long term sites",
 '_showvalues'        : True,
 '_format'            : '%.0f',
 'lbTitleString'      : "[years]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_contour(lons, lats, vals, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
os.system("xv tmp.png")
