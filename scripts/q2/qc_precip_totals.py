"""
Look at differences in precip totals between the hourly and 24h files
"""
import netCDF4
import mx.DateTime
import numpy
import numpy.ma
import os

def make_fp_long(tile, gts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile%s/data/QPESUMS/grid/q2rad_hsr_nc/long_qpe/%s00.nc" % (
        gts.strftime("%Y/%m/%d"), tile, 
        gts.strftime("%Y%m%d-%H%M") )

def make_fp(tile, gts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile%s/data/QPESUMS/grid/q2rad_hsr_nc/short_qpe/%s00.nc" % (
        gts.strftime("%Y/%m/%d"), tile, 
        gts.strftime("%Y%m%d-%H%M") )

sts = mx.DateTime.DateTime(2012,5,16,13)
ets = mx.DateTime.DateTime(2012,5,17,12)
interval = mx.DateTime.RelativeDateTime(hours=1)
now = sts
# Total up hourly data
total = None
while now <= ets:
    ncfp = make_fp(6,now)
    if not os.path.isfile(ncfp):
        print 'Missing', ncfp
        now += interval
        continue
    nc = netCDF4.Dataset(ncfp)
    hsr = nc.variables["rad_hsr_1h"][:] / 10.0
    if total is None:
        total = numpy.where(hsr > 0, hsr, 0)
    else:
        total += numpy.where(hsr > 0, hsr, 0)
    nc.close()
    now += interval
    
# Long
ncfp = make_fp_long(6, ets)
if not os.path.isfile(ncfp):
    print 'Missing', ncfp
nc = netCDF4.Dataset(ncfp)
hsr = nc.variables["rad_hsr_24h"][:] / 10.0
total -= numpy.where(hsr > 0, hsr, 0)
nc.close()
print numpy.max(total), numpy.min(total)
print numpy.sum(numpy.where(total < -1, 1, 0))

total = numpy.ma.array( total )
total.mask = numpy.where( total > -0.01, True, False )

import matplotlib.pyplot as plt

fig, ax = plt.subplots(1,1)
ax.set_title("tile6 difference 24-hourly minus 24h\n12z 16 May - 12z 17 May 2012")

res = ax.imshow(total)
fig.colorbar(res)

fig.savefig('test.png')