from scipy import stats
import psycopg2
import numpy
import datetime
from pyiem import reference
from pyiem.plot import MapPlot
import matplotlib.pyplot as plt
import network
import pytz
from pyiem.plot import maue
maue()

today = datetime.datetime.now()
today = today.replace(tzinfo=pytz.timezone("UTC"))
    
POSTGIS = psycopg2.connect(database='postgis', user='nobody', host='iemdb')
cursor = POSTGIS.cursor()

def run(nexrad):
    drct = []
    sknt = []
    doy = []
    minvalid = None
    for yr in range(2005, 2014):
        if minvalid is None:
            cursor.execute("""SELECT min(valid) from  nexrad_attributes_"""+`yr`+"""
            WHERE nexrad = %s 
            """ , (nexrad,))
            row = cursor.fetchone()
            if row[0] is not None:
                minvalid = row[0]
        cursor.execute("""
     SELECT drct, sknt, extract(doy from valid) from nexrad_attributes_"""+`yr`+""" WHERE
     nexrad = %s and sknt > 0
    """, (nexrad,))
        print nexrad, yr, cursor.rowcount
        for row in cursor:
            drct.append( row[0] )
            sknt.append( row[1] )
            doy.append( row[2] )
    
    years = (today - minvalid).days / 365.25
    (fig, ax) = plt.subplots(2,1, figsize=(9,7), dpi=100)
    
    H2, xedges, yedges = numpy.histogram2d(drct, sknt, bins=(36,15), range=[[0,360],[0,70]])
    res = ax[0].pcolormesh(xedges, yedges, H2.transpose() / years, cmap='maue')
    fig.colorbar(res, ax=ax[0])
    ax[0].set_xlim(0,360)
    ax[0].set_ylabel("Storm Speed [kts]")
    ax[0].set_xticks( (0,90,180,270,360) )
    ax[0].set_xticklabels( ('N','E','S','W','N') )
    ax[0].set_title("%s - 5 Jun 2013 K%s NEXRAD Storm Attributes Histogram\n%s unique attributes + volume scan, units are ~ attributes/year" % (
                                        minvalid.strftime("%d %b %Y"), nexrad, len(drct),))
    ax[0].grid(True)
    
    H2, xedges, yedges = numpy.histogram2d(doy, drct, bins=(36,36), range=[[0,365],[0,360]])
    res = ax[1].pcolormesh(xedges, yedges, H2.transpose() / years, cmap='maue')
    fig.colorbar(res, ax=ax[1])
    ax[1].set_ylim(0,360)
    ax[1].set_ylabel("Movement Direction")
    ax[1].set_yticks( (0,90,180,270,360) )
    ax[1].set_yticklabels( ('N','E','S','W','N') )
    ax[1].set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
    ax[1].set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
    ax[1].set_xlim(0,365)
    ax[1].grid(True)
    
    ax[1].set_xlabel("Generated 6 June 2013 by Iowa Environmental Mesonet")
    
    fig.savefig('%s_histogram.png' % (nexrad,))
    
nt = network.Table(("NEXRAD", "TWDR"))
for sid in nt.sts.keys():
    run(sid)
