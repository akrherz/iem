# 

import sys, os
sys.path.append("../lib/")
import iemplot

import netCDF3
nc = netCDF3.Dataset('time.nc', 'r')
grid = nc.variables['data'][:] / 12.0
xaxis = nc.variables['longitude'][:]
yaxis = nc.variables['latitude'][:]

#---------- Plot the points

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 '_title'       : "October 23, 2009 Rainfall Duration",
 'lbTitleString': 'Hours',
}

iemplot.simple_grid_fill(xaxis, yaxis, grid, cfg)

os.system("convert -depth 8 -colors 128 -trim -border 5 -bordercolor '#fff' -resize 900x700 -density 120 tmp.ps temp.png")
#os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/gdd_norm_may1_pt.png bogus png' gdd_norm_may1_pt.png")
#os.remove("gdd_norm_may1_pt.png")
#os.remove("tmp.ps")
