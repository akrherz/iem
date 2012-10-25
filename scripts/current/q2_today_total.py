"""
Create a plot of today's total precipitation from the Stage4 estimates
"""

import netCDF4
import mx.DateTime
import iemplot
import numpy
import os
import sys
import Image
import tempfile
import subprocess
import cStringIO
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon

clevs = numpy.arange(0,0.2,0.05)
clevs = numpy.append(clevs, numpy.arange(0.2,1.0,0.1))
clevs = numpy.append(clevs, numpy.arange(1.0,5,0.25))
clevs = numpy.append(clevs, numpy.arange(5.0,10,1.0))
clevs[0] = 0.01
# Load color ramp
iemplot.maue(len(clevs))

def make_fp(ts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile2/data/QPESUMS/grid/q2rad_hsr_nc/short_qpe/%s00.nc" % (
        ts.gmtime().strftime("%Y/%m/%d"), 
        ts.gmtime().strftime("%Y%m%d-%H%M") )

def doday(ts):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    # First possible file we are interested in....
    sts = ts + mx.DateTime.RelativeDateTime(hour=1, minute=0)
    # Last possible file, base 5
    ets = ts - mx.DateTime.RelativeDateTime(minutes= (ts.minute%5))
    
    now = ets
    total = None
    lts = None
    lons = numpy.arange(-110., -89.995, 0.01) 
    lats = numpy.arange(55.0, 39.99, -0.01)
    ncvar = "rad_hsr_1h"
    divisor = 1.0
    interval = mx.DateTime.RelativeDateTime(minutes=5)

    while now > sts:
        if os.path.isfile(make_fp(now)):
            if lts is None:
                lts = now
            if now.minute == 0:
                ncvar = "rad_hsr_1h"
                divisor = 1.0
                interval = mx.DateTime.RelativeDateTime(hours=1)
            else:
                ncvar = "preciprate_hsr"
                divisor = 12.0
            #print "USING %s NCVAR %s DIVISOR %s" % (make_fp(now), 
            #                                        ncvar, divisor)
            nc = netCDF4.Dataset(make_fp(now))
            if nc.variables.has_key(ncvar):
                val = nc.variables[ncvar][:] / divisor
                if total is None:
                    total = numpy.where(val > 0, val, 0)
                    #total = val
                else:
                    total += numpy.where( val > 0, val, 0)
                    #total += val
            nc.close()
        now -= interval
    
    if total is None:
        return

    # Set some bogus values to keep from complaining about all zeros?
    total[10:20,10:20] = 20.
    
    fig = plt.figure(num=None, figsize=(10.24,7.68))
    fig.subplots_adjust(bottom=0, left=0, right=1, top=1, wspace=0, hspace=0)

    ax = plt.axes([0.01,0.05,0.9,0.85], axisbg=(0.4471,0.6235,0.8117))
    map = Basemap(projection='merc', fix_aspect=False,
        urcrnrlat=iemplot.IA_NORTH +0.1, llcrnrlat=iemplot.IA_SOUTH, 
        urcrnrlon=iemplot.IA_EAST, llcrnrlon=iemplot.IA_WEST, 
        lon_0=-95.0, lat_0=40, lat_1=42, lat_2=45,
             resolution='i', ax=ax)
    map.fillcontinents(color='1.0',zorder=0)
    
    x, y = numpy.meshgrid(lons, lats)
    px, py = map(x, y)
    cl = iemplot.LevelColormap(clevs,cmap=cm.get_cmap('maue'))
    cl.set_under('#000000')
    cs = map.contourf(px,py, total / 254.0, clevs, 
            cmap=cl, zorder=1)
    cbar = map.colorbar(cs, location='right', pad="1%", ticks=cs.levels)
    cbar.set_label('inch')

    #map.drawstates(zorder=2)
    shp_info = map.readshapefile('/mesonet/data/gis/static/shape/4326/iowa/iacounties', 'c')
    for nshape,seg in enumerate(map.c):
        poly=Polygon(seg,fill=False,ec='k',zorder=2, lw=.4)
        ax.add_patch(poly)
    
    map.drawstates(linewidth=2, zorder=3)
    
    fig.text(0.13, 0.94, "NMQ Q2 Today's Precipitation [inch]", fontsize=18)
    fig.text(0.13, 0.91, 'Total up to %s' % (
        (lts - mx.DateTime.RelativeDateTime(minutes=1))
        .strftime("%d %B %Y %I:%M %p %Z"),))

    logo = Image.open('../../htdocs/images/logo_small.png')
    ax3 = plt.axes([0.02,0.89,0.1,0.1], frameon=False, axisbg=(0.4471,0.6235,0.8117), yticks=[], xticks=[])
    ax3.imshow(logo, origin='lower')
    
    fig.text(0.01, 0.03, "Iowa Environmental Mesonet, generated %s" % (
                        mx.DateTime.now().strftime("%d %B %Y %I:%M %p %Z"),))
    
    ram = cStringIO.StringIO()
    plt.savefig(ram, format='png')
    ram.seek(0)
    im = Image.open(ram)
    im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
    tmpfp = tempfile.mktemp()
    im2.save( tmpfp , format='PNG')
    
    pqstr = "plot ac %s00 iowa_q2_1d.png iowa_q2_1d.png png" % (
            ts.strftime("%Y%m%d%H"), )
    subprocess.call("/home/ldm/bin/pqinsert -p '%s' %s" % (pqstr, tmpfp), 
                    shell=True)
    os.unlink(tmpfp)
    
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        doday(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
    else:
        doday(mx.DateTime.now())
