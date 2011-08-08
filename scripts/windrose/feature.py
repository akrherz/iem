import Ngl
import numpy
import mx.DateTime
import datetime
import tempfile
import os
import sys
from windrose.windrose import WindroseAxes
import matplotlib
import matplotlib.image as image
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import iemdb

def windrose(station, database='asos', fp=None, months=numpy.arange(1,13),
    hours=numpy.arange(0,24), sts=datetime.datetime(1900,1,1),
    ets=datetime.datetime(2050,1,1)):
    """
    Create a standard windrose plot that we can all happily use
    """
    # Query metadata
    db = iemdb.connect('mesosite', bypass=True)
    mcursor = db.cursor()
    mcursor.execute("""SELECT name from stations where id = %s""" ,(station,))
    row = mcursor.fetchall()
    sname = row[0][0]
    mcursor.close()
    db.close()

    # Query observations
    db = iemdb.connect(database, bypass=True)
    acursor = db.cursor()
    acursor.execute("""SELECT sknt, drct, valid from alldata WHERE station = %s
        and sknt >= 0 and drct >= 0 and valid > %s and valid < %s""", (
        station, sts, ets))
    sknt = []
    drct = []
    for row in acursor:
        if row[2].month not in months or row[2].hour not in hours:
            continue
        if len(sknt) == 0:
            minvalid = row[2]
            maxvalid = row[2]
        sknt.append( row[0] * 1.15 ) 
        drct.append( row[1] )
        if row[2] < minvalid:
            minvalid = row[2]
        if row[2] > maxvalid:
            maxvalid = row[2]
    acursor.close()
    db.close()
    # Convert to numpy arrays
    sknt = numpy.array( sknt )
    drct = numpy.array( drct )
    # Generate figure
    fig = plt.figure(figsize=(3, 4), dpi=80, facecolor='w', edgecolor='w')
    rect = [0.1, 0.2, 0.7, 0.7]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    ax.bar(drct, sknt, normed=True, bins=(1,2,5,7,10,15,20), opening=0.8, edgecolor='white')
    #l = ax.legend(borderaxespad=-0.1)
    #plt.setp(l.get_texts(), fontsize=8)
    #ax.set_title("Ames [KAMW] Windrose Plot")
    handles = []
    for p in ax.patches_list[1:]:
        color = p.get_facecolor()
        handles.append( Rectangle((0, 0), 0.1, 0.3,
                    facecolor=color, edgecolor='black'))
    l = fig.legend( handles, ('2-5','5-7','7-10','10-15','15-20','20+') , loc=3,
     ncol=3, title='Wind Speed [mph]', mode=None, columnspacing=0.9, 
     handletextpad=0.45)
    plt.setp(l.get_texts(), fontsize=6)
    # Now we put some fancy debugging info on the plot
    tlimit = "Time Domain: "
    if len(hours) == 24 and len(months) == 12:
        tlimit = "All Year"
    if len(hours) < 24:
        for h in hours: 
            tlimit += "%s," % (datetime.datetime(2000,1,1,h).strftime("%I %P"),)
    if len(months) < 12:
        for h in months: 
            tlimit += "%s," % (datetime.datetime(2000,h,1).strftime("%b"),)
    label = "%s [%s] Windrose Plot\n[%s]\nPeriod of Record: %s - %s\nNumber of Obs: %s   Calm: %.1f%%   Avg Speed: %.1f mph" % (sname, station, tlimit,
        minvalid.strftime("%d %b %Y"), maxvalid.strftime("%d %b %Y"), 
        len(sknt), 
        numpy.sum( numpy.where(sknt < 2., 1., 0.)) / float(len(sknt)) * 100.,
        numpy.average(sknt))
    plt.gcf().text(0.17,0.89, "1-20 April 2011 Ames ")
    # Make a logo
    im = image.imread('/mesonet/www/apps/iemwebsite/htdocs/images/logo_small.png')
    #im[:,:,-1] = 0.8

    plt.figimage(im, 10, 625)

    if fp is not None:
        plt.savefig(fp)
    else:
        print "Content-Type: image/png\n"
        plt.savefig( sys.stdout, format='png' )
   
    del sknt, drct, im

windrose('AMW', sts=datetime.datetime(2011,4,1), ets=datetime.datetime(2011,5,1), fp='test.png')
