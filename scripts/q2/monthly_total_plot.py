"""
 Create a monthly total plot of Q2 Estimates
"""
import mx.DateTime
import os
import sys
import numpy
import nmq
import iemplot

def plotdata(data, sts, ets, midwest=False):
    """
    Generate the plot
    """
    if midwest:
        ul_x, ul_y = nmq.get_image_xy(iemplot.MW_WEST, iemplot.MW_NORTH)
        lr_x, lr_y = nmq.get_image_xy(iemplot.MW_EAST, iemplot.MW_SOUTH)
        dg = 0.1
        fn = "midwest"
    else:
        ul_x, ul_y = nmq.get_image_xy(iemplot.IA_WEST, iemplot.IA_NORTH)
        lr_x, lr_y = nmq.get_image_xy(iemplot.IA_EAST, iemplot.IA_SOUTH)
        dg = 0.02
        fn = "iowa"
    dgd = dg * 100
    sample = data[ul_y:lr_y:dgd, ul_x:lr_x:dgd]
    sample = numpy.flipud(sample)
    sample = sample  * 2.0 / 25.4
 
    if midwest:
        lats = numpy.arange(iemplot.MW_SOUTH, iemplot.MW_NORTH, dg)
        lons = numpy.arange(iemplot.MW_WEST, iemplot.MW_EAST, dg)
    else:
        lats = numpy.arange(iemplot.IA_SOUTH, iemplot.IA_NORTH, dg)
        lons = numpy.arange(iemplot.IA_WEST, iemplot.IA_EAST, dg)
    now = mx.DateTime.now()
    cfg = {
        'cnLevelSelectionMode': "ExplicitLevels",
        #'cnLevels' : [0.01,0.25,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5,6,7,10],
        'cnLevels': numpy.percentile( sample[numpy.nonzero(sample)], [1,5,10,15,25,40,50,60,75,85,90,95,99]),
         'wkColorMap': 'WhiteBlueGreenYellowRed',
         '_midwest': midwest,
        'nglSpreadColorStart': 2,
        'nglSpreadColorEnd'  : -1,
        '_MaskZero'          : True,
        'lbTitleString': '[inch]',
        '_title': '%s NMQ Q2 Precipitation Estimate' % (ts.strftime("%B %Y"),),
        '_valid': '%s 12 AM to %s 12 AM' % (sts.strftime("%-d %b %Y"), 
                                            ets.strftime("%-d %b %Y")),
    }
    tmpfp = iemplot.simple_grid_fill(lons, lats, sample, cfg)
    pqstr = "plot %s %s summary/month/q2_%s_total_precip.png %s/summary/q2_%s_total_precip.png png" % (
                                    'cm', sts.strftime("%Y%m%d%H%M"), fn,  
                                                              sts.strftime("%Y/%m"), fn)
    thumbpqstr = "plot %s %s summary/month/q2_%s_total_precip_thumb.png %s/summary/q2_%s_total_precip.png png" % (
                                    'c', sts.strftime("%Y%m%d%H%M"), fn,  
                                                              sts.strftime("%Y/%m"), fn)
    iemplot.postprocess(tmpfp, pqstr, thumb=True, thumbpqstr=thumbpqstr)

if __name__ == '__main__':
    ts = mx.DateTime.now()
    sts = mx.DateTime.DateTime(ts.year, ts.month, 1, 0, 0)
    ets = sts + mx.DateTime.RelativeDateTime(months=1)
    if ets > mx.DateTime.now():
        ets = mx.DateTime.now()
    data = nmq.get_precip( sts, ets )
    if data is None:
        sys.exit()
    plotdata(data, sts, ets)
    plotdata(data, sts, ets, midwest=True)