import numpy
import iemdb
import datetime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

maxt = {12: numpy.zeros( (366,), 'f'),
        24: numpy.zeros( (366,), 'f'),
        36: numpy.zeros( (366,), 'f')}

memt= {12: [], 24: [], 36: []}
memv = {12: [], 24: [], 36: []}

acursor.execute("""
 SELECT valid, tmpf from t2012 where station = 'DSM' and tmpf > -99
 ORDER by valid ASC
""")

for row in acursor:
    v = row[0]
    t = row[1]
    
    for hr in [12,24,36]:
        while len(memv[hr]) > 0 and ((v - memv[hr][-1]) > datetime.timedelta(hr/24, 3600 * (hr%24))):
            memv[hr].pop()
            memt[hr].pop()
        memt[hr].insert(0,  t )
        memv[hr].insert(0, v )
        delta = max(memt[hr]) - min(memt[hr])
        if delta > maxt[hr][ int(v.strftime("%j")) - 1]:
            maxt[hr][ int(v.strftime("%j")) - 1] = delta
      
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.scatter( numpy.arange(1,367), maxt[12], marker='+', color='g', label='12 hr')
ax.scatter( numpy.arange(1,367), maxt[24], marker='o', color='r', label='24 hr')
ax.scatter( numpy.arange(1,367), maxt[36], marker='s', color='b', label='36 hr')
ax.legend( ncol=3)
ax.set_title("Des Moines Maximum Temperature Change [1933-2012]")

ax.set_ylim(0, max(maxt[36])+10)
ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_ylabel("Temperature Change $^{\circ}\mathrm{F}$")
ax.set_xlabel("Day of Year")
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')