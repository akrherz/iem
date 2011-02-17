# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot, numpy
import Nio

for hr in range(3,75,3):
  grib = Nio.open_file('/tmp/nam.t00z.awip3d%02i.tm00.grib2' % (hr,), 'r')
  if hr == 3:
    tot = grib.variables['APCP_P8_L1_GLC0_acc'][:]
    lats = grib.variables['gridlat_0'][:]
    lons = grib.variables['gridlon_0'][:]
  else:
    tot += grib.variables['APCP_P8_L1_GLC0_acc3h'][:]
  grib.close()


cfg = {
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 0.25,
 'cnMinLevelValF'       : 0.25,
 'cnMaxLevelValF'       : 3.0,
 'cnFillMode'		: 'CellFill',
 'wkColorMap': 'WhViBlGrYeOrRe',
 '_title'             : "NAM 72 Hour Precipitation Forecast",
 '_valid'             : "30 Jan 6 PM Forecast till 6 PM 2 Feb 2010",
 'lbTitleString'      : "[inch]",
 '_midwest'		: True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_grid_fill(lons, lats, tot / 25.4, cfg)
import iemplot
iemplot.makefeature(tmpfp)
#iemplot.postprocess(tmpfp, "")
