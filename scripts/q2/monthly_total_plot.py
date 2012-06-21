"""
 Create a monthly total plot of Q2 Estimates
"""
import mx.DateTime
import os
import osgeo.gdal as gdal
import numpy
import nmq
import iemplot

def getdata(sts, ets):
    """
    Generate a monthly plot of Q2 estimates based on some fancy pants
    logic
    """
    # Figure out our period


    pointer = sts
    
    # Figure out which files we have available to make this work
    files = []
    for dayint in [3,1]:
        now = pointer + mx.DateTime.RelativeDateTime(days=dayint)
        while now <= ets:
            gmt = now.gmtime()
            fp = gmt.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/q2/p"+ 
                               ` 24*dayint ` +"h_%Y%m%d%H00.png")
            if os.path.isfile(fp):
                files.append( fp )
                pointer = now
            now += mx.DateTime.RelativeDateTime(days=dayint)

    if len(files) == 0:
        print 'No Data Available for Q2 monthly_total_plot.py'
        return None
    # Now we have files to loop over and add precip data too!
    total = None
    for file in files:
        img = gdal.Open(file, 0)
        data = img.ReadAsArray() # 3500, 7000 (y,x) staring upper left I think
        if total is None:
            total = data
        else:
            total += data
        del img
        
    return total
    
def plotdata(data, sts, ets):
    """
    Generate the plot
    """
    ul_x, ul_y = nmq.get_image_xy(iemplot.IA_WEST, iemplot.IA_NORTH)
    lr_x, lr_y = nmq.get_image_xy(iemplot.IA_EAST, iemplot.IA_SOUTH)
    sample = data[ul_y:lr_y:2, ul_x:lr_x:2]
    sample = numpy.flipud(sample)
    sample = sample  * 2.0 / 25.4
    
    lats = numpy.arange(iemplot.IA_SOUTH, iemplot.IA_NORTH, 0.02)
    lons = numpy.arange(iemplot.IA_WEST, iemplot.IA_EAST, 0.02)
    now = mx.DateTime.now()
    
    cfg = {
        'cnLevelSelectionMode': "ExplicitLevels",
        'cnLevels' : [0.01,0.25,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5,6,7,10],
         'wkColorMap': 'WhiteBlueGreenYellowRed',
        'nglSpreadColorStart': 2,
        'nglSpreadColorEnd'  : -1,
        '_MaskZero'          : True,
        'lbTitleString': '[inch]',
        '_title': '%s NMQ Q2 Precipitation Estimate' % (ts.strftime("%B %Y"),),
        '_valid': '%s 12 AM to %s 12 AM' % (sts.strftime("%-d %b %Y"), 
                                            ets.strftime("%-d %b %Y")),
    }
    tmpfp = iemplot.simple_grid_fill(lons, lats, sample, cfg)
    pqstr = "plot %s %s summary/q2_iowa_total_precip.png %s/summary/q2_iowa_total_precip.png png" % (
                                    'cm', sts.strftime("%Y%m%d%H%M"), 
                                                              sts.strftime("%Y/%m"),)
    iemplot.postprocess(tmpfp, pqstr)
    
ts = mx.DateTime.now()
sts = mx.DateTime.DateTime(ts.year, ts.month, 1, 0, 0)
ets = sts + mx.DateTime.RelativeDateTime(months=1)
if ets > mx.DateTime.now():
    ets = mx.DateTime.now()
data = getdata( sts, ets )
if data is None:
    sys.exit()
plotdata(data, sts, ets)