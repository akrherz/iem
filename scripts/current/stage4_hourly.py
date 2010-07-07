# Plot one hour stage4 data, please

import sys, os, random
sys.path.append("../lib/")
import iemplot, network

import mx.DateTime
import Nio

def doit(ts):
  """
  Generate hourly plot of stage4 data
  """
  gmtnow = mx.DateTime.gmt()
  routes = "a"
  if (gmtnow - ts).hours < 2:
    routes = "ac"

  fp = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.01h.grib" % (
      ts.strftime("%Y/%m/%d"), ts.strftime("%Y%m%d%H") )

  grib = Nio.open_file(fp)
  lats = grib.variables["g5_lat_0"][:]
  lons = grib.variables["g5_lon_1"][:]
  vals = grib.variables["A_PCP_GDS5_SFC_acc1h"][:] / 25.4

  cfg = {
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     'lbTitleString'      : "[inch]",
     '_valid'    : 'Hour Ending %s' % (ts.localtime().strftime("%d %B %Y %I %p"),),
     '_title'    : "StageIV 1 Hour Precipitation [inch]",
  }

  tmpfp = iemplot.simple_grid_fill(lons, lats, vals, cfg)
  pqstr = "plot %s %s00 iowa_stage4_1h.png iowa_stage4_1h_%s.png png" % (
    routes, ts.strftime("%Y%m%d%H"), ts.strftime("%H"))
  iemplot.postprocess(tmpfp, pqstr)

  # Plot Midwest
  cfg = {
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     '_midwest'           : True,
     'lbTitleString'      : "[inch]",
     '_valid'    : 'Hour Ending %s' % (ts.localtime().strftime("%d %B %Y %I %p"),),
     '_title'    : "StageIV 1 Hour Precipitation [inch]",
  }

  tmpfp = iemplot.simple_grid_fill(lons, lats, vals, cfg)
  pqstr = "plot %s %s00 midwest_stage4_1h.png midwest_stage4_1h_%s.png png" % (
      routes, ts.strftime("%Y%m%d%H"),ts.strftime("%H") )
  iemplot.postprocess(tmpfp, pqstr)


if len(sys.argv) == 5:
    ts = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) )
    doit( ts )
else:
    ts = mx.DateTime.gmt()
    doit( ts )
    doit( (ts - mx.DateTime.RelativeDateTime(hours=24)) )
    doit( (ts - mx.DateTime.RelativeDateTime(hours=48)) )
