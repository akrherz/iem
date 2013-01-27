import iemdb
import math
import network
nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS','AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS'))

vals = []
lats = []
lons = []
for line in open('wchill2.txt'):
    tokens = line.split(",")
    if len(tokens) < 2 or float(tokens[1]) < 100 or line[0] == '#':
        continue
    lats.append( nt.sts[tokens[0]]['lat'] )
    lons.append( nt.sts[tokens[0]]['lon'] )
    #vals.append( float(tokens[1]) )
    vals.append( float(tokens[1]) / float(tokens[2]) / 24.0 )

import iemplot

cfg = {'_midwest': True,
  '_showvalues': False,
    'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 'cnLevelSelectionMode': 'ManualLevels',
  'cnLevelSpacingF'      : 5.0,
 '_title': 'Hours of Sub-Zero ~S~o~N~F Wind Chill per Year, expressed in days',
 '_valid': 'Based on automated data between 1973-2012',
 'cnMinLevelValF'       : 0.0,
 'cnMaxLevelValF'       : 50.0,
  'lbTitleString': 'Days',
  '_format': '%.0f'}

tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)

