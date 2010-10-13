# Test to generate a map for a basin, please

import shapelib
import dbflib
import iemplot
import numpy
import netCDF3
import mx.DateTime
import sys

def make_fp(gts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile2/data/QPESUMS/grid/q2rad_hsr_nc/short_qpe/%s00.nc" % (
        gts.strftime("%Y/%m/%d"), 
        gts.strftime("%Y%m%d-%H%M") )

def doit(gts, i):

    shp = shapelib.open('squaw.shp', 'r')
    dbf = dbflib.DBFFile('squaw.dbf', 'r')

    shape = numpy.array( shp.read_object(0).vertices()[0] )
    # We have our outline
    lats = shape[:,1]
    lons = shape[:,0]

    # load up data
    dlons = numpy.arange(-110., -89.99, 0.01) 
    dlats = numpy.arange(55.0, 39.99, -0.01)

    nc = netCDF3.Dataset(make_fp(gts))
    val = nc.variables["preciprate_hsr"][:]

    cfg = { 
       'mpMinLonF'  : min(lons), 
       'mpMaxLonF'  : max(lons),
       'mpMinLatF'  : min(lats),
       'mpMaxLatF'  : max(lats),
       '_drawx'     : [lons],
       '_drawy'     : [lats],
       'cnFillMode' : 'RasterFill',
    'cnLevelSelectionMode': "ExplicitLevels",
    'cnLevels' : [0.01,0.05,0.1,0.25,0.5,0.75,1,1.25,1.5,2.0,2.5,3,4],
     'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
     'nglSpreadColorEnd'  : 2,
     '_MaskZero'          : True,
     'lbTitleString'      : "[inch/hr]",
     '_valid'    : 'Valid %s' % (
        gts.localtime().strftime("%d %B %Y %I:%M %p %Z"),),
     '_title'    : "NMQ Q2 Precipitation Rate over Squaw River Basin [inch/hr]",
     }

    # Scale factor is 10
    tmpfp = iemplot.simple_grid_fill(dlons, dlats, val / 254.0, cfg)
    fn = "frames/%05d.png" % (i,)
    iemplot.postprocess(tmpfp, '', fname=fn)
    nc.close()

if len(sys.argv) == 6:
    doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), 
                              int(sys.argv[3]),
                              int(sys.argv[4]), int(sys.argv[5])), 0)
