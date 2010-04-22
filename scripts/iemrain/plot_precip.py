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
}
# Generates tmp.ps
tmpfp = iemplot.simple_grid_fill(nc.variables['lon'][:], nc.variables['lat'][:], grid, cfg)

pqstr = "plot c 000000000000 summary/gdd_mon.png bogus png"
iemplot.postprocess(tmpfp, pqstr)
