# Number of days since the last 0.25 inch rainfall

import sys, os, random
sys.path.append("../lib/")
import iemplot, numpy
import Nio

grib = Nio.open_file('gfs.t12z.pgrbf240.grib2', 'r')
tmpf = ( grib.variables['TMP_P0_L103_GLL0'][:]  - 273.0 ) * (9.0/5.0) + 32.0


cfg = {
# 'cnLevelSelectionMode' : 'ManualLevels',
# 'cnLevelSpacingF'      : 2.0,
# 'cnMinLevelValF'       : 32.0,
# 'cnMaxLevelValF'       : 44.0,
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
iemplot.simple_grid_fill(grib.variables['lon_0'][:], grib.variables['lat_0'][:], tmpf, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
if os.environ["USER"] == "akrherz":
  os.system("xv tmp.png")
#os.remove("tmp.png")
#os.remove("tmp.ps")
