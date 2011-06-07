# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot, numpy
import Nio, mx.DateTime

#for hr in range(3,75,3):
#  grib = Nio.open_file('/tmp/nam.t00z.awip3d%02i.tm00.grib2' % (hr,), 'r')
#  if hr == 3:
#    tot = grib.variables['APCP_P8_L1_GLC0_acc'][:]
#    lats = grib.variables['gridlat_0'][:]
#    lons = grib.variables['gridlon_0'][:]
#  else:
#    tot += grib.variables['APCP_P8_L1_GLC0_acc3h'][:]
#  grib.close()

grib = Nio.open_file('nam.t00z.awip3d72.tm00.grib2', 'r')
lats = grib.variables['gridlat_0'][:]
lons = grib.variables['gridlon_0'][:]
#vals = grib.variables['CAPE_P0_L1_GLC0'][:]
RHV = grib.variables['RH_P0_L103_GLC0'][:]
RH = grib.variables['RH_P0_L103_GLC0']
TK = grib.variables['TMP_P0_L103_GLC0'][:]
DK = TK / (1+ 0.000425 * TK * -(numpy.log10(RHV/100.0)) ) 
DWPF = (DK - 273.15) * 9.0/5.0 + 32.0

ts0 = mx.DateTime.strptime(RH.initial_time, '%m/%d/%Y (%H:%M)')
ts0 = ts0 - mx.DateTime.RelativeDateTime(hours=5)
ts = ts0 + mx.DateTime.RelativeDateTime(hours=RH.forecast_time[0])

cfg = {
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 4.,
 'cnMinLevelValF'       : 20.,
 'cnMaxLevelValF'       : 70.0,
 'nglSpreadColorEnd': 2,
 'nglSpreadColorStart': -1,
# 'cnFillMode'		: 'CellFill',
 'wkColorMap': 'WhViBlGrYeOrRe',
 '_title'             : "NAM Forecasted Near Surface Dew Point",
 '_valid'             : "%s Forecast for %s" % (
      ts0.strftime("%-I %p %-d %B %Y"), ts.strftime("%-I %p %-d %B %Y")),
 'lbTitleString'      : "[F]",
 '_midwest'		: True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_grid_fill(lons, lats, DWPF, cfg)
import iemplot
iemplot.makefeature(tmpfp)
#iemplot.postprocess(tmpfp, "")
