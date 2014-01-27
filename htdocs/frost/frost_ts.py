#!/usr/bin/env python
import sys
import os
os.environ[ 'HOME' ] = '/tmp/'
os.environ[ 'USER' ] = 'nobody'
import matplotlib
matplotlib.use( 'Agg' )
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import cgi
import netCDF4
import datetime
import pytz
import numpy as np
from pyiem.datatypes import temperature

def get_times(nc):
    ''' Return array of datetimes for the time array '''
    tm = nc.variables['time']
    sts = datetime.datetime.strptime(tm.units.replace('minutes since ', ''), 
                                     '%Y-%m-%d %H:%M:%S')
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    res = []
    for t in tm[:]:
        res.append( sts + datetime.timedelta(minutes=float(t)))
    return res

def get_ij(lon, lat, nc):
    ''' Figure out the closest grid cell '''
    dist = ((nc.variables['lon'][:] - lon)**2 + 
            (nc.variables['lat'][:] - lat)**2)**.5
    return np.unravel_index(np.argmin(dist), dist.shape)

def process(lon, lat):
    ''' Generate a plot for this given combination '''
    (fig, ax) = plt.subplots(1,1)
    
    nc = netCDF4.Dataset("/mesonet/share/frost/201401270000_iaoutput.nc")
    times = get_times(nc)
    i, j = get_ij(lon, lat, nc)
    
    ax.plot(times, temperature(nc.variables['bdeckt'][:,i,j],'K').value('F'),
            color='k', label='Bridge Deck Temp')
    ax.plot(times, temperature(nc.variables['tmpk'][:,i,j], 'K').value("F"),
            color='r', label='Air Temp')
    ax.plot(times, temperature(nc.variables['dwpk'][:,i,j], 'K').value("F"),
            color='g', label='Dew Point')
    ax.set_ylim(-30,150)
    ax.set_title("i: %s j:%s" % (i, j))
    ax.xaxis.set_major_locator(
                               mdates.DayLocator(interval=1,
                                        tz=pytz.timezone("America/Chicago"))
                               )
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%Y',
                                        tz=pytz.timezone("America/Chicago")))
    ax.grid(True)
    ax.legend(loc='best')
    sys.stdout.write("Content-Type: image/png\n\n")
    fig.savefig( sys.stdout, format="png")

    

if __name__ == '__main__':
    form = cgi.FieldStorage()
    if form.has_key('lon') and form.has_key('lat'):
        process(float(form.getfirst('lon')), float(form.getfirst('lat')))