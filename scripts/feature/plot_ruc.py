# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot, numpy
import Nio

grib = Nio.open_file('/tmp/ruc2.t12z.pgrb20f09.grib2', 'r')
print grib.variables.keys()
cape = grib.variables['CAPE_P0_L1_GLC0'][:]


cfg = {
# 'cnLevelSelectionMode' : 'ManualLevels',
# 'cnLevelSpacingF'      : 2.0,
# 'cnMinLevelValF'       : 32.0,
# 'cnMaxLevelValF'       : 44.0,
 'wkColorMap': 'WhViBlGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_midwest': 1,
 '_title'             : "RUC Surface Convective Available Potential Energy",
 '_valid'             : "7 AM Forecast for 4 PM 14 July 2010",
 'lbTitleString'      : "[J/kg]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_grid_fill(grib.variables['gridlon_0'][:], grib.variables['gridlat_0'][:], cape, cfg)
iemplot.postprocess(tmpfp, "")
