import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

doy = []
cnt = []
yr = []
colors = []

def d(v):
    if v < 180:
        v += 365
    return v

def c(ts):
    if ts.year == 2013 or (ts.year == 2012 and ts.month > 6):
        return 'k'
    if ts.year == 2012 or (ts.year == 2011 and ts.month > 6):
        return 'r'
    return 'c'

ccursor.execute("""SELECT day, extract(doy from day), high 
    from alldata where station = 'IA2203' ORDER by day ASC""")
alive = 0
for row in ccursor:
    if row[2] < 50:
        alive += 1
    elif row[2] >= 50 and alive > 1: # Streak ends
        doy.append( d(row[1]) )
        cnt.append( alive )
        yr.append( row[0].year  )
        colors.append( c(row[0]) )
        alive = 0
    else:
        alive = 0


import matplotlib.pyplot as plt
import matplotlib.font_manager
import numpy
prop = matplotlib.font_manager.FontProperties(size=10) 
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(doy, cnt, c=colors, edgecolor='None', marker='s')
for mydoy,mycnt, myyr in zip(doy, cnt, yr):
   if mycnt > 120 or (mycnt > 80 and mydoy > 449) or (mycnt > 20 and mydoy > 454 and mycnt < 40):
      print mydoy, mycnt, myyr
      ax.text(mydoy, mycnt, "%s" % (myyr,), va='top')
ax.grid(True)
ax.set_xlabel("Date when streak ended, red 2011-2012, black 2012-2013")
ax.set_ylabel("Number of Days")
ax.set_ylim(0,140)
ax.set_xlim(265,500)
ax.set_title("Des Moines (1880-2013) Streak of Days(2+) below 50$^{\circ}\mathrm{F}$")
ax.set_xticks( (274,305,335,365,365+32,365+60,365+91,365+121) )
ax.set_xticklabels( ('Oct 1','Nov 1', 'Dec 1', 'Jan 1', 'Feb 1', 'Mar 1', 'Apr 1','May 1'))
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')   
