#!/usr/bin/env python
import sys
import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cgi
import netCDF4
import datetime
import pytz
import numpy as np
from pyiem.datatypes import temperature

def get_latest_time(model):
    ''' Figure out the latest model runtime '''
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.timezone("UTC"))
    utc = utc.replace(hour=12,minute=0,second=0,microsecond=0)
    limit = 24
    while not os.path.isfile(
                utc.strftime("/mesonet/share/frost/"+model+"/%Y%m%d%H%M_iaoutput.nc")):
        utc -= datetime.timedelta(hours=12)
        limit -= 1
        if limit < 0:
            return None
    return utc 

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

def get_icond_color(val):
    if val is None or val == -1:
        return 'none'
    colors = ['white', 'tan', 'orange', 'blue', 'purple', 'green']
    try:
        return colors[val]
    except:
        return 'none'

def get_ifrost_color(val):
    if val is None or val == -1:
        return 'none'
    colors = ['#EEEEEE', 'r']
    try:
        return colors[val]
    except:
        return 'none'

def process(model, lon, lat):
    ''' Generate a plot for this given combination '''
    (fig, ax) = plt.subplots(1,1)
    modelts = get_latest_time(model)
    if modelts is None:
        ax.text(0.5, 0.5, "No Data Found to Plot!", ha='center')
        sys.stdout.write("Content-Type: image/png\n\n")
        fig.savefig( sys.stdout, format="png")
        return
    nc = netCDF4.Dataset(
            modelts.strftime("/mesonet/share/frost/"+model+"/%Y%m%d%H%M_iaoutput.nc"),'r')
    times = get_times(nc)
    i, j = get_ij(lon, lat, nc)
    
    ax.plot(times, temperature(nc.variables['bdeckt'][:,i,j],'K').value('F'),
            color='k', label='Bridge Deck Temp' if model == 'bridget' else 'Pavement')
    ax.plot(times, temperature(nc.variables['tmpk'][:,i,j], 'K').value("F"),
            color='r', label='Air Temp')
    ax.plot(times, temperature(nc.variables['dwpk'][:,i,j], 'K').value("F"),
            color='g', label='Dew Point')
    #ax.set_ylim(-30,150)
    ax.set_title(("ISUMM5 %s Timeseries\n"
                 +"i: %s j:%s lon: %.2f lat: %.2f Model Run: %s") % (model,
                    i, j, nc.variables['lon'][i,j], nc.variables['lat'][i,j],
                    modelts.astimezone(pytz.timezone("America/Chicago")).strftime(
                            "%-d %b %Y %-I:%M %p")))
    
    ax.xaxis.set_major_locator(
                               mdates.DayLocator(interval=1,
                                        tz=pytz.timezone("America/Chicago"))
                               )
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%Y',
                                        tz=pytz.timezone("America/Chicago")))
    ax.axhline(32, linestyle='-.')
    ax.grid(True)
    ax.set_ylabel("Temperature $^\circ$F")
    ax.legend(loc='best')

    (ymin, ymax) = ax.get_ylim()

    for i2, ifrost in enumerate(nc.variables['ifrost'][:-1,i,j]):
        ax.barh(ymax-1, 1.0/24.0/4.0, left=times[i2], 
                fc=get_ifrost_color(ifrost), ec='none')
    for i2, icond in enumerate(nc.variables['icond'][:-1,i,j]):
        ax.barh(ymax-2, 1.0/24.0/4.0, left=times[i2], 
                fc=get_icond_color(icond), ec='none')
        
    
    sys.stdout.write("Content-Type: image/png\n\n")
    fig.savefig( sys.stdout, format="png")

def main():
    """ Go Main Go """
    form = cgi.FieldStorage()
    if form.has_key('lon') and form.has_key('lat'):
        process(form.getfirst('model'), float(form.getfirst('lon')), 
                float(form.getfirst('lat')))    

if __name__ == '__main__':
    # main
    main()
