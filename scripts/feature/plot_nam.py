# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot, numpy
import Nio

for hr in range(3,51,3):
  grib = Nio.open_file('/tmp/nam.t18z.awip3d%02i.tm00.grib2' % (hr,), 'r')
  if hr == 3:
    tot = grib.variables['APCP_P8_L1_GLC0_acc'][:]
    lats = grib.variables['gridlat_0'][:]
    lons = grib.variables['gridlon_0'][:]
  else:
    tot += grib.variables['APCP_P8_L1_GLC0_acc3h'][:]
  grib.close()


cfg = {
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 0.5,
 'cnMinLevelValF'       : 0.5,
 'cnMaxLevelValF'       : 13.0,
 'wkColorMap': 'WhViBlGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "NAM 48 Hour Precipitation Forecast",
 '_valid'             : "20 July 1 PM Forecast till 1 PM 22 July 2010",
 'lbTitleString'      : "[inch]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_grid_fill(lons, lats, tot / 25.4, cfg)
iemplot.postprocess(tmpfp, "")
