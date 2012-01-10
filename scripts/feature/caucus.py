import mx.DateTime
import numpy
import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

dates = [
         mx.DateTime.DateTime(1972,1,24),
         mx.DateTime.DateTime(1976,1,19),
         mx.DateTime.DateTime(1980,1,21),
         mx.DateTime.DateTime(1984,2,20),
         mx.DateTime.DateTime(1988,2,8),
         mx.DateTime.DateTime(1992,2,10),
         mx.DateTime.DateTime(1996,2,12),
         mx.DateTime.DateTime(2000,1,24),
         mx.DateTime.DateTime(2004,1,19),
         mx.DateTime.DateTime(2008,1,3),
         mx.DateTime.DateTime(2012,1,3),
         ]

tmpfs = []

for dt in dates:
    acursor.execute("""
    SELECT avg(tmpf) from t%s where station = 'DSM' and valid BETWEEN
    '%s 18:00' and '%s 20:00' and tmpf > -50
    """ % (dt.year, dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d")))
    row = acursor.fetchone()
    tmpfs.append( row[0] )
    
#tmpfs.append(34)
print tmpfs, len(dates), len(tmpfs)

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(numpy.arange(0, len(tmpfs))-0.4, tmpfs, fc='lightblue')
xlabels = []
for i in range(len(dates)):
    ax.text(i, tmpfs[i]+0.1, "%.0f$^{\circ}\mathrm{F}$" % (tmpfs[i],),
            va='bottom', ha='center')
    ax.text(i-0.15, tmpfs[i]-0.5, dates[i].strftime("%-d %b"), rotation=90,
            va='top')
    xlabels.append( dates[i].year )
ax.set_xticklabels( xlabels )
ax.set_xticks( numpy.arange(0, len(tmpfs)) )
ax.set_xlim(-0.5,11)
ax.set_ylim(0,41)
ax.set_title("Iowa Presidential Caucus Weather")
ax.set_ylabel("7 PM Temperature $^{\circ}\mathrm{F}$")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')