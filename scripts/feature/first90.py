import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

jday = []

ccursor.execute("""
 SELECT year, min(extract(doy from day)) from alldata where 
 stationid = 'ia2203' and high > 89 GROUP by year ORDER by year ASC
    """)
for row in ccursor:
  jday.append( row[1] )

jday.append(100)
print len(jday)
import matplotlib.pyplot as plt
import numpy as np
jday = np.array(jday)
fig = plt.figure()
ax = fig.add_subplot(111)
av = np.average(jday)
bars = ax.bar(np.arange(1893,2012)-0.4, jday, facecolor='r', edgecolor='r')
for bar in bars:
  if bar.get_height() > av:
    bar.set_facecolor('b')
    bar.set_edgecolor('b')
ax.plot([1893,2011], [av, av], color='black')
ax.grid(True)
ax.set_ylim(75,210)
ax.set_xlim(1892,2012)
yticks = []
ylabels = []
for i in range(75,210):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day in [1,8,15,22]:
    yticks.append(i)
    ylabels.append( ts.strftime("%d %B") )
ax.set_yticks(yticks)
ax.set_yticklabels(ylabels)
ax.set_title("First 90$^{\circ}\mathrm{F}$ for Des Moines [1893-2011]\n2011 ties 1930 with 10 April, 29 Mar 1986 earliest")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
