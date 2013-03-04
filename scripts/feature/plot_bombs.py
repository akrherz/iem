import iemplot

vals = []
lats = []
lons = []

for line in open('bombs.txt'):
    tokens = line.split(",")
    if len(tokens) < 4:
        continue
    if float(tokens[3]) > 100 or len(tokens[0]) == 4:
        print line,
        continue
    vals.append( float(tokens[3]) / 6.0 )    
    lats.append( float(tokens[2]) )
    lons.append( float(tokens[1]) )
    
cfg = {
#       '_conus': True,
        '_midwest': True,
       '_showvalues': True,
             'cnLevelSelectionMode' : 'ManualLevels',
      'cnLevelSpacingF'      : 1,
     'cnMinLevelValF'       : 0,
     'cnMaxLevelValF'       : 12,
       '_format': '%.1f',
       '_title': 'METAR Site: Frequency of 24mb Drop in MSLP within 24 hours',
       '_valid': '2007-2012 Events per Year, !!! THIS IS NOT BOMBOGENESIS !!!',
       'lbTitleString': 'events',
       }
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)
