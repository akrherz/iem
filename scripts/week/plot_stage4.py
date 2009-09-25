# Plot an accumulation of stage4 data!

import sys, os
sys.path.append("../lib/")
import Nio
import iemplot, numpy

import mx.DateTime
ets = mx.DateTime.now() + mx.DateTime.RelativeDateTime(minute=0)
sts = ets + mx.DateTime.RelativeDateTime(hour=1,days = -7)
interval = mx.DateTime.RelativeDateTime(hours=1)

now = sts
total = None
while now <= ets:
  fp = now.gmtime().strftime("/mnt/a1/ARCHIVE/data/%Y/%m/%d/stage4/ST4.%Y%m%d%H.01h.grib")
  if not os.path.isfile( fp ):
    now += interval
    continue
  grib = Nio.open_file( fp )
  data = grib.variables["A_PCP_GDS5_SFC_acc1h"][:] / 25.4
  if total is None:
    total = data
    lats = grib.variables["g5_lat_0"][:]
    lons = grib.variables["g5_lon_1"][:]
  else:
    total = total + data

  now += interval

mask = numpy.where( total < 0.02, True, False)
total = numpy.ma.array( total, mask=mask)

cfg = {
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 1.0,
 'cnMinLevelValF'       : 0,
 'cnMaxLevelValF'       : 12,
 'cnFillMode'         : 'CellFill',
 'wkColorMap'         : 'WhViBlGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_title'             : "Iowa NCEP Stage4 7 Day Rainfall Estimate",
 '_valid'             : "%s 12 AM - %s" % (sts.strftime("%d %B %Y"), ets.strftime("%d %B %Y %-I %p")),
 'lbTitleString'      : "[inch]",
 'pmLabelBarHeightF'  : 0.6,
 'pmLabelBarWidthF'   : 0.1,
 'lbLabelFontHeightF' : 0.025
}
# Generates tmp.ps
iemplot.simple_grid_fill(lons, lats, total, cfg)

os.system("convert -rotate -90 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 +repage tmp.ps tmp.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/7day/stage4.png bogus png' tmp.png")
if os.environ["USER"] == "akrherz":
  os.system("xv tmp.png")
os.remove("tmp.png")
os.remove("tmp.ps")
