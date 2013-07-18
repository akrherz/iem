import psycopg2
import pyiem.meteorology as met
import pyiem.datatypes as dt
import numpy as np
import matplotlib.pyplot as plt


ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = ASOS.cursor()

cursor.execute("""
  SELECT valid, tmpf, dwpf from alldata where station = 'DSM' and
  tmpf >= 80 and dwpf > -50 and valid > '1935-01-01'
  and (extract(minute from valid) = 0 or extract(minute from valid) > 52)
""")

hits3 = np.zeros( (2014-1935), 'f')
hits5 = np.zeros( (2014-1935), 'f')
total = np.zeros( (2014-1935), 'f')
for row in cursor:
    t = dt.temperature(row[1], 'F')
    d = dt.temperature(row[2], 'F')
    hdx = met.heatindex(t, d)
    
    if (hdx.value("F") - 3) >= row[1]:
        hits3[ row[0].year - 1935 ] += 1.0
    if (hdx.value("F") - 5) >= row[1]:
        hits5[ row[0].year - 1935 ] += 1.0
    total[ row[0].year - 1935 ] += 1.0


(fig, ax) = plt.subplots(2,1, sharex=True)

val = hits3 / total * 100.0
avg = np.average(val)
bars = ax[0].bar(np.arange(1935,2014)-0.4, val , ec='b', fc='b')
ax[0].plot([1933,2013], [avg,avg], c='k')
for bar in bars:
    if bar.get_height() > avg:
        bar.set_facecolor("r")
        bar.set_edgecolor("r")
ax[0].grid(True)
#ax[0].set_ylim(0, )
ax[0].set_title("1935-2013 Des Moines Humidity Effect on Heat Index\nWhen Air Temp over 80$^\circ$F, Frequency of Heat Index Change")
ax[0].set_ylabel(r"Frequency [%] of 3+$\Delta ^\circ$F")

val = hits5 / total * 100.0
avg = np.average(val)
bars = ax[1].bar(np.arange(1935,2014)-0.4, val , ec='b', fc='b')
ax[1].plot([1933,2013], [avg,avg], c='k')
for bar in bars:
    if bar.get_height() > avg:
        bar.set_facecolor("r")
        bar.set_edgecolor("r")
ax[1].grid(True)
#ax[0].set_ylim(0, )
ax[1].set_ylabel(r"Frequency [%] of 5+ $\Delta ^\circ$F")
ax[1].set_xlim(1934.5,2013.5)
ax[1].set_xlabel("*2013 through 18 July, colors are above/below long term avg")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
