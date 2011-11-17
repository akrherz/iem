#!/mesonet/python/bin/python
"""
Create a generic mapper of IEMRE data
$Id$:
"""
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import os
os.environ[ 'HOME' ] = '/tmp/'
os.environ[ 'USER' ] = 'nobody'

try:
    import netCDF4 as netCDF3
except:
    import netCDF3

import numpy
import numpy.ma
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap, BoundaryNorm

import iemre
import cgi
import mx.DateTime
import Image

def setup_plot(ctx):
    """
    Create a standardized basemap plot
    @param ctx context dictionary
    """
    ctx['fig'] = plt.figure(num=None, figsize=(8.0,6.0), frameon=True, facecolor='#FFFFFF')
    
    ctx['plotax'] = plt.axes([0.01,0.1,0.9,0.8], axisbg=(0.4471,0.6235,0.8117))
    
    ctx['map'] = Basemap(
        llcrnrlon=ctx['llcrnrlon'],llcrnrlat=ctx['llcrnrlat'],
        urcrnrlon=ctx['urcrnrlon'],urcrnrlat=ctx['urcrnrlat'],
            resolution='l',area_thresh=1000.,projection='merc',
            ax=ctx['plotax'])

    #ctx['map'].fillcontinents(color='0.7',zorder=0,ax=ctx['plotax'])
    ctx['map'].drawstates(ax=ctx['plotax'],zorder=2,linewidth=1)
    ctx['map'].drawcoastlines(ax=ctx['plotax'],zorder=2)
    ctx['map'].drawcountries(ax=ctx['plotax'],zorder=2)

def main():
    # White balanced
    colors = [(0,       0,       0),
        (24 ,     24   ,   112),
       ( 16 ,     78   ,   139),
      (  23  ,    116  ,   205),
      (  72 ,     118  ,   255),
      (  91 ,     172  ,   237),
      (  173 ,    215 ,    230),
      (  209 ,    237  ,   237),
      (  229 ,    239 ,    249),
      (  242 ,    255   ,  255),
      (  253 ,    245  ,   230),
      (  255 ,    228 ,    180),
      (  243 ,    164  ,   96),
      (  237 ,    118  ,   0),
      (  205 ,    102  ,   29),
      (  224  ,   49  ,    15),
      (  237 ,    0   ,    0),
      (  205 ,    0  ,     0),
      (  139 ,    0 ,      0)]
    colors = numpy.array(colors) / 255.0
    colors = ["#FFFFFF", "#7FFF00", "#00CD00", "#008B00", "#104E8B", "#1E90FF",
              "#00B2EE", "#00EEEE", "#8968CD", "#912CEE", "#8B008B", "#8B0000",
              "#CD0000", "#EE4000", "#FF7F00", "#CD8500", "#FFD700", "#EEEE00",
              "#FFFF00", "#7FFF00","#000000"]
    cmap = ListedColormap(colors[1:])
    cmap.set_over(color=colors[-1])
    cmap.set_under(color=colors[-1])
    #values = numpy.arange(0,10,0.25)
    #values = [0.01,0.05,0.1,0.25,0.5,0.75,1.0,1.25,1.5,1.75,2.0,2.5,3.0,4.0,5.0,7.5,10.0]
    values = [0.01,0.10,0.25,0.50,1.0,1.5,2.0,2.5,3.0,4.0,5.0,7.5,10.0,12.5,15.0,17.5,20.0]
    normer = BoundaryNorm(values, cmap.N, clip=False)

    ctx = {}
    
    nc = netCDF3.Dataset('/mesonet/data/iemre/2010_mw_hourly.nc', 'r')
    lon = nc.variables['lon'][:]
    lat = nc.variables['lat'][:]
    ctx['llcrnrlon'] = numpy.min(lon)
    ctx['llcrnrlat'] = numpy.min(lat)
    ctx['urcrnrlon'] = numpy.max(lon)
    ctx['urcrnrlat'] = numpy.max(lat)
    setup_plot(ctx)
    
    idx = iemre.hour_idx( mx.DateTime.DateTime(2011,6,1,1,5) )
    idx2 = iemre.hour_idx( mx.DateTime.DateTime(2011,7,1,1,5) )
    tmpk = numpy.ma.array( numpy.sum(nc.variables['p01m'][idx:idx2,:,:],0) ) / 25.4
    
    #nx = int((ctx['map'].xmax-ctx['map'].xmin)/40000.)+1
    #ny = int((ctx['map'].ymax-ctx['map'].ymin)/40000.)+1
    #rm_tmpk,x,y = ctx['map'].transform_scalar(tmpk,nc.variables['lon'],
    #                                          nc.variables['lat'],nx,ny,
    #                                          returnxy=True,masked=True)
    #print 'Content-Type: text/plain\n'
    #print numpy.min(rm_tmpk), numpy.max(rm_tmpk)
    tmpk.mask = numpy.where(tmpk < 0.01, True, False)
    im = ctx['map'].imshow(tmpk, cmap=cmap,interpolation='nearest',norm=normer,zorder=1)
    
    cax = plt.axes([0.932,0.2,0.015,0.6])
    clr = ctx['fig'].colorbar(im, cax=cax, format='%g')
    clr.set_ticks(values)
    
    cax.text(-0.75, 0.5, 'Precipitation [inch]', transform=cax.transAxes,
    size='medium', color='k', horizontalalignment='center', 
    verticalalignment='center', rotation='vertical')
    
    ctx['plotax'].text(0.05, -0.05, 'Test test test', ha='left', va='baseline',
                       transform=ctx['plotax'].transAxes)
    
    nc.close()
    print "Content-Type: image/png\n"
    ctx['fig'].savefig(sys.stdout, format='png', edgecolor='k')
    """
    ctx['fig'].canvas.draw()
    w,h = ctx['fig'].canvas.get_width_height()
    buf = numpy.fromstring ( ctx['fig'].canvas.tostring_rgb(), dtype=numpy.uint8 )
    buf.shape = ( w, h,3 )
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = numpy.roll ( buf, 3, axis = 2 )
    p = Image.fromstring( "RGB", ( w ,h ), buf.tostring( ) )
    p = p.convert("P", palette=Image.ADAPTIVE, colors=256)
    p.save(sys.stdout, 'PNG')
    """
    
if __name__ == '__main__':
    main()