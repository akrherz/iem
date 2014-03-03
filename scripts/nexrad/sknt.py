import psycopg2
import numpy as np
import datetime
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
    minvalid = datetime.datetime(2014,1,1)
    minvalid = minvalid.replace(tzinfo=pytz.timezone("UTC"))
    cursor.execute("""
 SELECT drct, sknt, extract(doy from valid), valid from nexrad_attributes_log WHERE
 nexrad = %s and sknt > 0
""", (nexrad,))
    for row in cursor:
        drct.append( row[0] )
        sknt.append( row[1] )
        doy.append( row[2] )
        if row[3] < minvalid:
            minvalid = row[3]
    print nexrad, cursor.rowcount, minvalid
    
    years = (today - minvalid).days / 365.25
    (fig, ax) = plt.subplots(2,1, figsize=(9,7), dpi=100)
    
    H2, xedges, yedges = np.histogram2d(drct, sknt, bins=(36,15), range=[[0,360],[0,70]])
    res = ax[0].pcolormesh(xedges, yedges, H2.transpose() / years, cmap='maue')
    fig.colorbar(res, ax=ax[0])
    ax[0].set_xlim(0,360)
    ax[0].set_ylabel("Storm Speed [kts]")
    ax[0].set_xticks( (0,90,180,270,360) )
    ax[0].set_xticklabels( ('N','E','S','W','N') )
    ax[0].set_title("%s - %s K%s NEXRAD Storm Attributes Histogram\n%s unique attributes + volume scan, units are ~ attrs/year" % (
                                        minvalid.strftime("%d %b %Y"), 
                                        today.strftime("%d %b %Y"), nexrad, len(drct),))
    ax[0].grid(True)
    
    H2, xedges, yedges = np.histogram2d(doy, drct, bins=(36,36), range=[[0,365],[0,360]])
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
    
    ax[1].set_xlabel("Generated %s by Iowa Environmental Mesonet" % (today.strftime("%d %b %Y"),))
    
    fig.savefig('%s_histogram.png' % (nexrad,))

if __name__ == '__main__':
    ''' See how we are called '''
    nt = network.Table(("NEXRAD", "TWDR"))
    for sid in nt.sts.keys():
        run(sid)
