# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot, numpy
import Nio, mx.DateTime
import mesonet

#for hr in range(3,75,3):
#  grib = Nio.open_file('/tmp/nam.t00z.awip3d%02i.tm00.grib2' % (hr,), 'r')
#  if hr == 3:
#    tot = grib.variables['APCP_P8_L1_GLC0_acc'][:]
#    lats = grib.variables['gridlat_0'][:]
#    lons = grib.variables['gridlon_0'][:]
#  else:
#    tot += grib.variables['APCP_P8_L1_GLC0_acc3h'][:]
#  grib.close()

grib = Nio.open_file('nam.t00z.conusnest.hiresf60.tm00.grib2', 'r')
lats = grib.variables['gridlat_0'][:]
lons = grib.variables['gridlon_0'][:]
#CAPE = grib.variables['CAPE_P0_L1_GLC0'][:]
#RHV = grib.variables['RH_P0_L103_GLC0'][:]
RH = grib.variables['RH_P0_L103_GLC0']
TK = grib.variables['TMP_P0_L103_GLC0'][:]
#DK = TK / (1+ 0.000425 * TK * -(numpy.log10(RHV/100.0)) ) 
#DWPF = (DK - 273.15) * 9.0/5.0 + 32.0
TMPF = mesonet.k2f( TK )

ts0 = mx.DateTime.strptime(RH.initial_time, '%m/%d/%Y (%H:%M)')
ts0 = ts0 - mx.DateTime.RelativeDateTime(hours=5)
ts = ts0 + mx.DateTime.RelativeDateTime(hours=RH.forecast_time[0])

cfg = {
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 1.0,
 'cnMinLevelValF'       : 18,
 'cnMaxLevelValF'       : 45,
 'nglSpreadColorEnd': -1,
 'nglSpreadColorStart': 2,
# 'cnFillMode'		: 'CellFill',
 'wkColorMap': 'WhViBlGrYeOrRe',
 '_title'             : "NAM 2 meter AGL Air Temperature for Sunday Morning",
 '_valid'             : "%s Forecast for %s" % (
      ts0.strftime("%-I %p %-d %B %Y"), ts.strftime("%-I %p %-d %B %Y")),
 'lbTitleString'      : "F",
 #'_midwest'		: True,
}
# Generates tmp.ps
tmpfp = iemplot.simple_grid_fill(lons, lats, TMPF, cfg)
import iemplot
iemplot.makefeature(tmpfp)
#iemplot.postprocess(tmpfp, "")
