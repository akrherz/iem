import netCDF4
import numpy
import mx.DateTime

offset1 = int((mx.DateTime.DateTime(2012,5,1) - mx.DateTime.DateTime(2012,1,1)).days)
offset2 = int((mx.DateTime.DateTime(2012,6,6) - mx.DateTime.DateTime(2012,1,1)).days)

nc = netCDF4.Dataset("/mesonet/data/iemre/2012_mw_daily.nc", 'r')
p01d = nc.variables['p01d']

ncc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
cp01d = ncc.variables['p01d']
for i in range(offset1,offset2):
  if cp01d[i,5,5] > 20:
    print i, p01d[i,5,5], cp01d[i,5,5]

diff = (numpy.sum(p01d[offset1:offset2,:,:],0) -  numpy.sum(cp01d[offset1:offset2,:,:],0)) / 25.4
print numpy.sum(p01d[offset1:offset2,5,5]), numpy.sum(cp01d[offset1:offset2,5,5])
print numpy.max(diff), numpy.min(diff)

cfg = {'_title': '1 May - 6 June 2012 Precipitation Departure from Normal',
       '_valid': '1 May - 6 June 2012',
       #'cnFillMode': 'CellFill',
       '_midwest': True,
 'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 1.,
 'cnMinLevelValF'       : -7.,
 'cnMaxLevelValF'       : 7.,
       'wkColorMap' : 'hotcolr_19lev',
        'nglSpreadColorStart': -1,
        'nglSpreadColorEnd'  : 2,
       'lbTitleString': '[inch]'}

import iemplot
tmpfp = iemplot.simple_grid_fill(nc.variables['lon'][:], nc.variables['lat'][:], diff, cfg)
iemplot.makefeature(tmpfp)

nc.close()
ncc.close()
