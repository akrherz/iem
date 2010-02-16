# Number of days since the last 0.25 inch rainfall

import sys, os, random, lib
sys.path.append("../lib/")
import iemplot, numpy

import mx.DateTime
now = mx.DateTime.now()
#now = mx.DateTime.DateTime(1997,5,1)

nc = lib.load_netcdf( now )
precipitation = nc.variables['precipitation']

t0 = 95 * 19
t1 = 96 * 23
grid = numpy.sum( precipitation[t0:t1,:,:], 0) / 25.4
grid = numpy.where( grid < 0.02, -9, grid )

cfg = {
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 0.5,
 'cnMinLevelValF'       : 0,
 'cnMaxLevelValF'       : 4,
 'wkColorMap': 'WhViBlGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa Rainfall",
 '_valid'             : "1 Sep 2009  - 5 Sep 2009",
 'lbTitleString'      : "[inch]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_grid_fill(nc.variables['lon'][:], nc.variables['lat'][:], grid, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
if os.environ["USER"] == "akrherz":
  os.system("xv tmp.png")
#os.remove("tmp.png")
#os.remove("tmp.ps")
