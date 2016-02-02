import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import datetime
import numpy as np
import psycopg2
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()

dates = [
         datetime.date(1972, 1, 24),
         datetime.date(1976, 1, 19),
         datetime.date(1980, 1, 21),
         datetime.date(1984, 2, 20),
         datetime.date(1988, 2, 8),
         datetime.date(1992, 2, 10),
         datetime.date(1996, 2, 12),
         datetime.date(2000, 1, 24),
         datetime.date(2004, 1, 19),
         datetime.date(2008, 1, 3),
         datetime.date(2012, 1, 3),
         datetime.date(2016, 2, 1),
         ]

# First entry has 3 hourly data, it may have been blowing snow!
tmpfs = [5, ]

for dt in dates:
    acursor.execute("""
    SELECT valid, tmpf, metar, presentwx from t%s where
    station = 'DSM' and valid BETWEEN
    '%s 18:50' and '%s 19:10' and tmpf > -50
    """ % (dt.year, dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d")))
    for i, row in enumerate(acursor):
        print i, dt, row[2]
        if i == 0:
            tmpfs.append(row[1])

tmpfs.append(36)
print tmpfs, len(dates), len(tmpfs)


fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(np.arange(0, len(tmpfs))-0.4, tmpfs, fc='lightblue')
xlabels = []
for i in range(len(dates)):
    ax.text(i, tmpfs[i]+0.1, "%.0f$^{\circ}\mathrm{F}$" % (tmpfs[i],),
            va='bottom', ha='center')
    ax.text(i-0.15, tmpfs[i]-0.5, dates[i].strftime("%-d %b"), rotation=90,
            va='top')
    xlabels.append(dates[i].year)
ax.set_xticklabels(xlabels)
ax.set_xticks(range(0, len(tmpfs)))
ax.set_xlim(-0.5, 12)
ax.set_ylim(0, 41)
ax.set_title("Iowa Presidential Caucus - 7 PM Des Moines Airport Temperature")
ax.set_ylabel("7 PM Temperature $^{\circ}\mathrm{F}$")
fig.savefig('test.png')
