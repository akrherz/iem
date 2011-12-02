import netCDF4 
import numpy
import mx.DateTime

offset1 = int((mx.DateTime.DateTime(2011,9,1) - mx.DateTime.DateTime(2011,1,1)).days)
offset2 = int((mx.DateTime.DateTime(2011,10,22) - mx.DateTime.DateTime(2011,1,1)).days)

nc = netCDF4.Dataset("/mesonet/data/iemre/2011_mw_daily.nc", 'r')
p01d = nc.variables['p01d']

ncc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')
cp01d = ncc.variables['p01d']

diff = numpy.sum(p01d[offset1:offset2,:,:],0) /  numpy.sum(cp01d[offset1:offset2,:,:],0) * 100.


cfg = {'_title': 'Precipitation Departure from Normal',
       '_valid': '1 September through 22 Oct 2011',
       'cnFillMode': 'CellFill',
       '_midwest': True,
       #'wkColorMap' : 'BlueWhiteOrangeRed',
        'nglSpreadColorStart': -1,
        'nglSpreadColorEnd'  : 2,
       'lbTitleString': '[%]'}

import iemplot
tmpfp = iemplot.simple_grid_fill(nc.variables['lon'][:], nc.variables['lat'][:], diff, cfg)
iemplot.makefeature(tmpfp)

nc.close()
ncc.close()