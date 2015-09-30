import ephem
import psycopg2
import datetime
import numpy as np

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

moon = ephem.Moon()
myloc = ephem.Observer()
myloc.lat = '41.99206'
myloc.long = '-93.62183'

def s2dt(s):
    ''' Convert ephem string to datetime instance '''
    return datetime.datetime.strptime(str(s), '%Y/%m/%d %H:%M:%S')

def run():
    ''' Get the first fall sub 29 and when the nearest full moon was that year
    '''
    cursor.execute(''' SELECT year, min(day), min(extract(doy from day))
    from alldata_ia where
    station = 'IA0200' and low < 29 and month > 6 GROUP by year ORDER
    by year ASC''')
    juliandays = []
    moondiff = []
    for row in cursor:
        juliandays.append( row[2] )
        myloc.date = "%s/%s/%s" % (row[1].year, row[1].month, row[1].day)
        
        lastd = s2dt(ephem.previous_full_moon(myloc.date)).date()
        today = row[1]
        nextd = s2dt(ephem.next_full_moon(myloc.date)).date()
        forward = (nextd - today).days
        backward = (today - lastd).days
        if backward == forward:
            moondiff.append(backward)
        elif backward < forward:
            moondiff.append( backward )
        elif forward < backward:
            moondiff.append( 0 - forward)
            
    return moondiff, juliandays

import matplotlib.pyplot as plt
        
moondiff, juliandays = run()
juliandays = np.array(juliandays)

(fig, ax) = plt.subplots(1,1)
ax.scatter(moondiff, juliandays, marker='x', s=40)
ax.set_title("1893-2012 Ames First Fall sub 29$^\circ$F Temperature")
ax.set_ylabel("Date")
ax.set_xlabel("Days to nearest Full Moon")
ax.set_yticks( (258,265,274,281, 288, 295, 305, 312, 319) )
ax.set_xlim(-16,16)
ax.axhline(np.average(juliandays), linestyle='-.', lw=2, color='r')
ax.set_yticklabels( ('Sep 15', 'Sep 22', 'Oct 1', 'Oct 8', 'Oct 15', 'Oct 22', 'Nov 1', 'Nov 8', 'Nov 15') )

ax.grid(True)
fig.savefig('test.png')
