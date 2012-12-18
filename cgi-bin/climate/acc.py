#!/usr/bin/env python
"""
 Plot accumulated stuff
  1. Accumulated GDD
  2. Accumulated Precip
  3. Accumulated SDD
"""
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import os
os.environ[ 'HOME' ] = '/tmp/'
os.environ[ 'USER' ] = 'nobody'
import cgi

import numpy
import mx.DateTime
import matplotlib
matplotlib.use( 'Agg' )
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

import network
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

def get_data(station, startdt, enddt):
    """ Get data for this period of choice, please """
    ccursor.execute("""
    SELECT o.day as oday, gdd50(o.high, o.low) as ogdd50, c.gdd50 as cgdd50,
    o.precip as oprecip, c.precip as cprecip, 
    sdd86(o.high, o.low) as ogdd86, c.sdd86 as csdd86
    from climate c JOIN alldata_"""+ station[:2] +""" o on
    (c.station = o.station and to_char(c.valid, 'mmdd') = o.sday)
    WHERE o.station = %s and o.day >= %s and o.day < %s and sday != '0229'
    ORDER by oday ASC
    """, (station, startdt.strftime("%Y-%m-%d"), enddt.strftime("%Y-%m-%d")))
    dates = []
    gdd50 = []
    d_gdd50 = []
    c_gdd50 = []
    gcount = 0
    gtotal = 0
    precip = []
    d_precip = []
    c_precip = []
    pcount = 0
    ptotal = 0
    sdd86 = []
    d_sdd86 = []
    c_sdd86 = []
    scount = 0
    stotal = 0
    cgtotal = 0
    cstotal = 0
    cptotal = 0
    for row in ccursor:
        dates.append( row[0] )
        gcount += (float(row[1]) - float(row[2]))
        pcount += (float(row[3]) - float(row[4]))
        scount += (float(row[5]) - float(row[6]))
        gtotal += float(row[1])
        ptotal += float(row[3])
        stotal += float(row[5])
        cgtotal += float(row[2])
        cptotal += float(row[4])
        cstotal += float(row[6])        
        gdd50.append( gtotal )
        precip.append( ptotal )
        sdd86.append( stotal )
    
        d_gdd50.append( gcount )
        d_precip.append( pcount )
        d_sdd86.append( scount )
        
        c_gdd50.append( cgtotal )
        c_sdd86.append( cstotal )
        c_precip.append( cptotal )
        
    return dates, gdd50, d_gdd50, c_gdd50, precip, d_precip, c_precip, sdd86, d_sdd86, c_sdd86

def process_cgi(form):
    """ Do the processing, please """
    startdt = mx.DateTime.DateTime(int(form.getvalue('syear', 2012)),
                                    int(form.getvalue('smonth', 5)),
                                    int(form.getvalue('sday', 1))
                                   )
    enddt = mx.DateTime.DateTime(int(form.getvalue('eyear', 2012)),
                                    int(form.getvalue('emonth', 10)),
                                    int(form.getvalue('eday', 1))
                                   )
    
    station = form.getvalue('station', 'IA0200')
    nt = network.Table("%sCLIMATE" % (station[:2],))
    dates, gdd50, d_gdd50, c_gdd50, precip, d_precip, c_precip, sdd86, d_sdd86, c_sdd86 = get_data(station,
                                                                startdt, enddt)
    
    (fig, ax) = plt.subplots(3,1, figsize=(9,12))
    
    ax[0].set_title("Accumulated GDD(base=50), Precip, & SDD(base=86)\n%s %s" % (
                                                        station, nt.sts[station]['name']),
                    fontsize=18)
    yearlabel = startdt.year
    if startdt.year != enddt.year:
        yearlabel = "%s-%s" % (startdt.year, enddt.year)
    
    ax[0].plot(dates, gdd50, color='r', label='%s' % (yearlabel,), lw=2)
    ax[0].plot(dates, c_gdd50, color='k', label='Climatology', lw=2)
    ax[0].set_ylabel("GDD Base 50 $^{\circ}\mathrm{F}$", fontsize=16)
    
    ax[1].plot(dates, precip, color='r', lw=2)
    ax[1].plot(dates, c_precip, color='k', lw=2)
    ax[1].set_ylabel("Precipitation [inch]", fontsize=16)
    
    ax[2].plot(dates, sdd86, color='r', lw=2)
    ax[2].plot(dates, c_sdd86, color='k', lw=2)
    ax[2].set_ylabel("SDD Base 86 $^{\circ}\mathrm{F}$", fontsize=16)

    ax[0].grid(True)
    ax[1].grid(True)
    ax[2].grid(True)
    
    ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
    ax[1].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
    ax[2].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))    
    if form.getvalue('year2'):
        startdt2 = mx.DateTime.DateTime(int(form.getvalue('year2')),
                                    int(form.getvalue('smonth', 5)),
                                    int(form.getvalue('sday', 1))
                                   )
        enddt2 = mx.DateTime.DateTime(int(form.getvalue('year2')) + (enddt.year - startdt.year),
                                    int(form.getvalue('emonth', 10)),
                                    int(form.getvalue('eday', 1))
                                   )
        
        dates2, gdd50, d_gdd50, c_gdd50, precip, d_precip, c_precip, sdd86, d_sdd86, c_sdd86 = get_data(station,
                                                                startdt2, enddt2)
    
        yearlabel = startdt2.year
        if startdt2.year != enddt2.year:
            yearlabel = "%s-%s" % (startdt2.year, enddt2.year)
        sz = len(dates)
        if len(gdd50) >= sz:
            ax[0].plot(dates, gdd50[:sz], label="%s" % (yearlabel,), color='b', lw=2)
            ax[1].plot(dates, precip[:sz], color='b', lw=2)
            ax[2].plot(dates, sdd86[:sz], color='b', lw=2)
    
    if form.getvalue('year3'):
        startdt3 = mx.DateTime.DateTime(int(form.getvalue('year3')),
                                    int(form.getvalue('smonth', 5)),
                                    int(form.getvalue('sday', 1))
                                   )
        enddt3 = mx.DateTime.DateTime(int(form.getvalue('year3')) + (enddt.year - startdt.year),
                                    int(form.getvalue('emonth', 10)),
                                    int(form.getvalue('eday', 1))
                                   )
        
        dates3, gdd50, d_gdd50, c_gdd50, precip, d_precip, c_precip, sdd86, d_sdd86, c_sdd86 = get_data(station,
                                                                startdt3, enddt3)
    
        yearlabel = startdt3.year
        if startdt3.year != enddt3.year:
            yearlabel = "%s-%s" % (startdt2.year, enddt2.year)
        sz = len(dates)
        if len(gdd50) >= sz:
            ax[0].plot(dates, gdd50[:sz], label="%s" % (yearlabel,), color='g', lw=2)
            ax[1].plot(dates, precip[:sz], color='g', lw=2)
            ax[2].plot(dates, sdd86[:sz], color='g', lw=2)
    
    ax[0].legend(loc=2, prop={'size': 14})

    fmt = form.getvalue('format', 'png')
    if fmt in ['eps',]:
        print "Content-Type: application/postscript\n"
    elif fmt in ['png',]:
        print "Content-Type: image/png\n"
    fig.savefig( sys.stdout, format=fmt )

if __name__ == '__main__':
    form = cgi.FieldStorage()
    if form.has_key("station"):
        process_cgi(form)