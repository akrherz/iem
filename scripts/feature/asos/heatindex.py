import psycopg2
import pyiem.meteorology as met
import pyiem.datatypes as dt
import numpy as np
import matplotlib.pyplot as plt


ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = ASOS.cursor()

cursor.execute("""
  SELECT valid, tmpf, dwpf from alldata where station = 'DSM' and
  tmpf > 80 and dwpf > 50 and valid > '1935-01-01'
""")

maxv = np.zeros( (2014-1935), 'f')
maxdoy = np.zeros( (2014-1935), 'f')
for row in cursor:
    t = dt.temperature(row[1], 'F')
    d = dt.temperature(row[2], 'F')
    hdx = met.heatindex(t, d)
    if hdx.value("F") > maxv[row[0].year - 1935]:
        maxv[ row[0].year - 1935 ] = hdx.value("F")
        maxdoy[ row[0].year - 1935 ] = int( row[0].strftime("%j") )


(fig, ax) = plt.subplots(2,1, sharex=True)

ax[0].bar(np.arange(1935,2014)-0.4, maxv, ec='r', fc='r')
ax[0].grid(True)
ax[0].set_ylim(95,125)
ax[0].set_title("1935-2013 Des Moines Heat Index")
ax[0].set_ylabel(r"Max Heat Index $^\circ$F")

ax[1].scatter(np.arange(1935,2014), maxdoy)
ax[1].set_xlim(1934.5, 2013.5)
ax[1].grid(True)
ax[1].set_yticks( (152,182,213,244,274) )
ax[1].set_yticklabels( ('Jun','Jul','Aug','Sep') )
ax[1].set_ylabel(r"Date of First Maximum")
ax[1].set_xlabel("* 2013 thru 8 July")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
