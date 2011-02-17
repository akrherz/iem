# 

import sys, os
sys.path.append("../lib/")
import iemplot

import netCDF3, numpy
nc = netCDF3.Dataset('time.nc', 'r')
grid = numpy.flipud( nc.variables['cnt'][:] / 12.0 )
xaxis = nc.variables['lons'][:]
yaxis = nc.variables['lats'][:]

#---------- Plot the points

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 '_title'       : "2 AM 9 Jan - 2 PM 11 Jan 2011 NEXRAD 0+ dBZ Time",
 'lbTitleString': 'Hours',
# '_midwest': True,
}

fp = iemplot.simple_grid_fill(xaxis, yaxis, grid, cfg)
#iemplot.postprocess(fp, '', '')
iemplot.makefeature(fp)