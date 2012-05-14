import netCDF3 as netCDF4
import numpy
import mx.DateTime

offset1 = int((mx.DateTime.DateTime(2011,1,1) - mx.DateTime.DateTime(2011,1,1)).days)
offset2 = int((mx.DateTime.DateTime(2012,1,1) - mx.DateTime.DateTime(2011,1,1)).days)

nc = netCDF4.Dataset("/mesonet/data/iemre/2011_mw_daily.nc", 'r')
p01d = nc.variables['p01d']

ncc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
cp01d = ncc.variables['p01d']
for i in range(offset1,offset2):
  if cp01d[i,5,5] > 20:
    print i, p01d[i,5,5], cp01d[i,5,5]

diff = (numpy.sum(p01d[offset1:offset2,:,:],0) -  numpy.sum(cp01d[offset1:offset2,:,:],0)) / 25.4
print numpy.sum(p01d[offset1:offset2,5,5]), numpy.sum(cp01d[offset1:offset2,5,5])
print numpy.max(diff), numpy.min(diff)

cfg = {'_title': '2011 Precipitation Departure from Normal',
       '_valid': '1 Jan - 31 Dec 2011',
       #'cnFillMode': 'CellFill',
       #'_midwest': True,
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 2.,
 'cnMinLevelValF'       : -14.,
 'cnMaxLevelValF'       : 14.,
       'wkColorMap' : 'hotcolr_19lev',
        'nglSpreadColorStart': -1,
        'nglSpreadColorEnd'  : 2,
       'lbTitleString': '[inch]'}

import iemplot
tmpfp = iemplot.simple_grid_fill(nc.variables['lon'][:], nc.variables['lat'][:], diff, cfg)
iemplot.makefeature(tmpfp)

nc.close()
ncc.close()
