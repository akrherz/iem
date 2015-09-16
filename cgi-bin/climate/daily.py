#!/usr/bin/env python
""" Generate a plot of daily climatology """
import cgi
import memcache
import sys
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg2
import numpy
import cStringIO
from PIL import Image
from pyiem.network import Table as NetworkTable
import datetime


def make_plot(station1, station2):
    """ Actually do the expense of making the plot! """
    nt = NetworkTable("IACLIMATE")
    
    dbconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
    cursor = dbconn.cursor()

    cursor.execute(""" SELECT valid, high, low from climate51 WHERE
     station = %s ORDER by valid ASC""", (station1,))
    highs = numpy.zeros( (cursor.rowcount))
    lows = numpy.zeros( (cursor.rowcount))
    valid = []
    for i, row in enumerate(cursor):
        highs[i] = row[1]
        lows[i] = row[2]
        valid.append( row[0] )
        subplots = 1
    
    subtitle = " 1951-%s\n[%s] %s " % (datetime.datetime.now().year, station1,
                                     nt.sts[station1]['name'])
    if station2:
        cursor.execute(""" SELECT valid, high, low from climate51 WHERE
         station = %s ORDER by valid ASC""", (station2,))
        highs2 = numpy.zeros( (cursor.rowcount))
        lows2 = numpy.zeros( (cursor.rowcount))
        valid2 = []
        for i, row in enumerate(cursor):
            highs2[i] = row[1]
            lows2[i] = row[2]
            valid2.append( row[0] )
        subplots = 2
        subtitle += " [%s] %s" % (station2, nt.sts[station2]['name'])
    (fig, ax) = plt.subplots(subplots, 1, sharex=True)
    if not station2:
        ax = [ax,]
        
    ax[0].plot(valid, highs, color='r', linestyle='-', label='%s High' % (station1,))
    ax[0].plot(valid, lows, color='b', label='%s Low' % (station1,))
    ax[0].set_ylabel(r"Temperature $^\circ\mathrm{F}$")
    ax[0].set_title("IEM Computed Daily Temperature Climatology"+subtitle)
    if station2:
        ax[0].plot(valid2, highs2, color='brown', label='%s High' % (station2,))
        ax[0].plot(valid2, lows2, color='green', label='%s Low' % (station2,))
        
        ax[1].plot(valid, highs - highs2, color='r', label='High Diff %s - %s' % (station1, station2))
        ax[1].plot(valid, lows - lows2, color='b', label='Low Diff')
        ax[1].set_ylabel(r"Temp Difference $^\circ\mathrm{F}$")
        ax[1].legend(fontsize=10, ncol=2, loc='best')
        ax[1].grid(True)
    
    ax[0].legend(fontsize=10, ncol=2, loc=8)
    ax[0].grid()
    ax[0].xaxis.set_major_locator(
                               mdates.MonthLocator(interval=1)
                               )
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))


def postprocess():
    ram = cStringIO.StringIO()
    plt.savefig(ram, format='png')
    ram.seek(0)
    im = Image.open(ram)
    im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
    ram = cStringIO.StringIO()
    im2.save( ram, format='png')
    ram.seek(0)
    return ram.read()

def main():
    """ Lets do this! """
    form = cgi.FieldStorage()
    station1 = form.getvalue('station1', 'IA0000')[:6]
    station2 = form.getvalue('station2', None)
    plottype = form.getvalue('plot', 'daily')
    year = int(form.getvalue('year', 0))
    if station2 is not None:
        station2 = station2[:6]
    
    mckey = "/cgi-bin/climate/daily.py|%s|%s|%s|%s" % (plottype, station1, 
                                                    station2, year)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    sys.stdout.write("Content-type: image/png\n\n")
    if not res:
        if plottype == 'daily':
            make_plot(station1, station2) 
        res = postprocess()
        mc.set(mckey, res, 86400)
    sys.stdout.write( res )

if __name__ == '__main__':
    main()
