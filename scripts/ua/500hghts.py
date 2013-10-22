'''
 Compute the difference between the 12 UTC 850 hPa temp and afternoon high
'''
from pyiem.datatypes import temperature
import psycopg2
import datetime
import numpy as np
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

rain500 = []
raintmpf = []
snow500 = []
snowtmpf = []
def run():
    pcursor.execute("""
 select valid, max(case when p.pressure = 500 then height else 0 end) - min(case when p.pressure = 1000 then height else 9999 end) from raob_profile p JOIN raob_flights f on 
 (p.fid = f.fid) where f.station in ('KOAX', 'KOVN', 'KOMA')  and 
 p.pressure in (1000,500) and extract(hour from valid at time zone 'UTC') in (0,12)
 GROUP by valid ORDER by valid ASC 
    """)
    for row in pcursor:
        valid = row[0]
        acursor.execute("""SELECT tmpf, p01i, presentwx from t"""+ str(valid.year) +"""
        WHERE station = 'OMA' and valid BETWEEN %s and %s and presentwx is not null
        """, (valid - datetime.timedelta(minutes=70), 
              valid + datetime.timedelta(minutes=70)))
        isnow = None
        irain = None
        for row2 in acursor:
            if row2[2].find("SN") > -1:
                isnow = row2[0]
            if row2[2].find("RA") > -1:
                irain = row2[0]
        
        if isnow is not None:
            snow500.append( row[1] )
            snowtmpf.append( isnow )
        if irain is not None:
            rain500.append( row[1] )
            raintmpf.append( irain )
        
    rain500 = np.array(rain500)
    snow500 = np.array(snow500)
    snowtmpf = np.array(snowtmpf)
    raintmpf = np.array(raintmpf)
    
    np.save('snowtmpf', snowtmpf)
    np.save('raintmpf', raintmpf)
    np.save('snow500', snow500)
    np.save('rain500', rain500)

snowtmpf = np.load('snowtmpf.npy')
snow500 = np.load('snow500.npy')
rain500 = np.load('rain500.npy')
raintmpf = np.load('raintmpf.npy')
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1, sharex=True)

ax[0].scatter(snowtmpf, snow500, marker='*', color='b', label='Snow', zorder=1)
ax[0].set_title("1961-2013 Omaha 1000-500 hPa Thickness and 2m Temps\nWhen Rain/Snow is reported within 1 Hour of sounding")
ax[0].set_ylim(4900,6000)
ax[0].set_ylabel("1000-500 hPa Thickness [m]")
ax[0].axhline(5400, c='k')
ax[0].axvline(32, c='k')
ax[0].grid(True)
ax[0].legend(loc=2)
ax[0].text(33,5050, "32$^\circ$F")

ax[1].scatter(raintmpf, rain500, facecolor='none', edgecolor='g', label='Rain', zorder=2)
ax[1].set_ylim(4900,6000)
ax[1].legend(loc=2)
ax[1].grid(True)
ax[1].set_xlabel("2 meter Air Temperature $^\circ$F")
ax[1].set_ylabel("1000-500 hPa Thickness [m]")
ax[1].axhline(5400, c='k')
ax[1].axvline(32, c='k')
ax[1].text(33,5050, "32$^\circ$F")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')