
import pg
import mx.DateTime

conn = pg.connect("coop", "iemdb", user="nobody")

rs = conn.query("SELECT day, high, low, precip from alldata where stationid = 'ia8706' and sday != '0229' and year >= 1893 ORDER by day ASC").dictresult()

hrecords = {}
hcnt = [0]*366
lcnt = [0]*366
lrecords = {}
precords = {}
pcnt = [0]*366


for row in rs:
  ts = mx.DateTime.strptime(row['day'], '%Y-%m-%d')
  doy = int(ts.strftime("%j"))
  if ts.year == 1893:
    hrecords[ ts.strftime("%m%d") ] = row['high']
    lrecords[ ts.strftime("%m%d") ] = row['low']
    precords[ ts.strftime("%m%d") ] = row["precip"]
    continue
  if row['precip'] > 0 and row['precip'] >= precords[ ts.strftime("%m%d") ]:
    precords[ ts.strftime("%m%d") ] = row['precip']
    pcnt[doy-1] += 1
    if doy == 46:
        print row
  if row['high'] >= hrecords[ ts.strftime("%m%d") ]:
    if ts.year > 1999:
      print ts, row['high'] - hrecords[ ts.strftime("%m%d") ]
    hrecords[ ts.strftime("%m%d") ] = row['high']
    hcnt[doy-1] += 1
  if row['low'] <= lrecords[ ts.strftime("%m%d") ]:
    lrecords[ ts.strftime("%m%d") ] = row['low']
    lcnt[doy-1] += 1



import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import iemplot

fig = plt.figure()
ax = fig.add_subplot(311)
rects = ax.bar( np.arange(0,366), hcnt, color='b', edgecolor='b')

#for i in range(len(rects)):
#    if rects[i].get_height() > expect[i]:
#        rects[i].set_facecolor('r')
#ax.plot( np.arange(1893,2011), expect, color='black', label="$365/n$")
#ax.set_ylim(0,50)
#ax.set_xlim(1893,2010)
ax.grid(True)

ax.set_ylabel("High Temp Records")
ax.set_title("Ames Daily Records Set Per Day")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)

#ax.text(1941, 22, "Max High Temperature")

ax = fig.add_subplot(312)
rects = ax.bar( np.arange(0,366), lcnt, color='r', edgecolor='r')
#for i in range(len(rects)):
#    if rects[i].get_height() > expect[i]:
#        rects[i].set_facecolor('b')
#ax.plot( np.arange(1893,2011), expect, color='black', label="$365/n$")
#ax.set_ylim(0,50)
#ax.set_xlim(1893,2010)
#ax.grid(True)

ax.set_ylabel("Low Temp Records")
#ax.text(1941, 22, "Min Low Temperature")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)
ax.grid(True)



ax = fig.add_subplot(313)
rects = ax.bar( np.arange(0,366), pcnt, color='b', edgecolor='b')
ax.set_ylabel("Precip Records")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)
ax.grid(True)


fig.savefig("test.png")
#iemplot.makefeature("test")
