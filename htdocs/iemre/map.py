#!/usr/bin/env python
"""
 Generate a map of one of the daily IEMRE variables
"""
import cgi
import memcache
import sys
import datetime
import netCDF4
from pyiem import iemre
from pyiem import plot
import numpy

def plot_daily(date, interval, plotvar, mc, mckey):
    """ Generate the plot, please """
    offset = iemre.daily_offset(date)
    
    nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (date.year,))
    p01d = nc.variables['p01d'][offset] / 25.4 # inches
    lons = nc.variables['lon'][:]
    lats = nc.variables['lat'][:]
    extra = lons[-1] + (lons[-1] - lons[-2])
    lons = numpy.concatenate([lons, [extra,]])

    extra = lats[-1] + (lats[-1] - lats[-2])
    lats = numpy.concatenate([lats, [extra,]])
    x,y = numpy.meshgrid(lons, lats)

    nc.close()

    p = plot.MapPlot(sector='midwest',
                 title='%s IEM Reanalysis Precipitation' % (date.strftime("%-d %b %Y"),)
                 )
    p.pcolormesh(x, y, p01d, numpy.arange(0,10.2,0.5))
    p.postprocess(web=True, memcache=mc, memcachekey=mckey, memcacheexpire=0)

def main():
    form = cgi.FieldStorage()
    date = form.getfirst('date', '20130101')
    interval = form.getfirst('type', 'daily')
    plotvar = form.getfirst('plot', 'precip_in')
    
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    mckey = "iemre/map/%s_%s_%s.png" % (interval, plotvar, date)
    res = mc.get(mckey)
    if res:
        sys.stdout.write("Content-type: image/png\n\n")
        sys.stdout.write( res )
        return
    # OK, we have plotting work yet to do
    date = datetime.datetime.strptime(date, '%Y%m%d')
    if interval == 'daily':
        plot_daily(date, interval, plotvar, mc, mckey)
        
if __name__ == '__main__':
    main()