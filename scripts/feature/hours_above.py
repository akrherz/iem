import iemdb
import math
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()


data = []
for yr in range(1933,2012):
    # Query out obs
    acursor.execute("""
    SELECT distinct to_char(valid, 'MMDDHH24') from t%s where station = 'DSM' 
    and tmpf >= 93 
    """ % (yr,))
    multi = 1.
    if yr > 1964 and yr < 1973:
        multi = 3.
    data.append( acursor.rowcount * multi)

data2 = []

for yr in range(1933,2012):
    ccursor.execute("""
    SELECT sum(sdd86(high,low)) from alldata_ia where year = %s and station = 'IA2203'
    """ % (yr))
    row = ccursor.fetchone()
    data2.append( row[0] )


import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(211)

ax.set_title("Des Moines Heat Stress [1933-2011]")

ax.bar( numpy.arange(1933,2012)-0.4, data, facecolor='r', edgecolor='r')
ax.set_ylabel("Hours Above 93$^{\circ}F$")
ax.set_xlim(1932.5,2011.5)
ax.grid(True)

ax2 = fig.add_subplot(212)
ax2.bar( numpy.arange(1933,2012)-0.4, data2, facecolor='r', edgecolor='r')
ax2.set_ylabel('Stress Degree Days')
ax2.grid(True)
ax2.set_xlim(1932.5,2011.5)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')