
import pg
import mx.DateTime

conn = pg.connect("coop", "iemdb", user="nobody")

rs = conn.query("""SELECT day, high, low, precip from alldata_ia 
  where station = 'IA0200' and sday != '0229' and year >= 1893 
  ORDER by day ASC""").dictresult()

hrecords = {}
hcnt = [0]*366
lcnt = [0]*366
lrecords = {}
precords = {}
pcnt = [0]*366


for row in rs:
    ts = mx.DateTime.strptime(row['day'], '%Y-%m-%d')
    doy = int(ts.strftime("%j"))
    sday = ts.strftime("%m%d")
    if ts.year == 1893:
        hrecords[ sday ] = row['high']
        lrecords[ sday ] = row['low']
        precords[ sday ] = row["precip"]
        continue
    if row['precip'] > 0 and row['precip'] >= precords[ sday ]:
        precords[ sday ] = row['precip']
        pcnt[doy-1] += 1
    if row['high'] >= hrecords[ sday ]:
        if ts.year > 1999:
            print ts, row['high'] - hrecords[ sday ]
        hrecords[ sday ] = row['high']
        hcnt[doy-1] += 1
    if row['low'] <= lrecords[ sday ]:
        lrecords[ sday ] = row['low']
        lcnt[doy-1] += 1



import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import iemplot

fig = plt.figure()
ax = fig.add_subplot(311)
rects = ax.bar( np.arange(0,366), hcnt, color='r', edgecolor='r')

#for i in range(len(rects)):
#    if rects[i].get_height() > expect[i]:
#        rects[i].set_facecolor('r')
#ax.plot( np.arange(1893,2011), expect, color='black', label="$365/n$")
#ax.set_ylim(0,50)
#ax.set_xlim(1893,2010)
ax.grid(True)

ax.set_ylabel("High Temp Records")
ax.set_title("1894-2013 Ames Daily Records Set or Tied Per Day")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)
ax.set_ylim(top=12)

#ax.text(1941, 22, "Max High Temperature")

ax = fig.add_subplot(312)
rects = ax.bar( np.arange(0,366), lcnt, color='b', edgecolor='b')
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
ax.set_ylim(top=12)



ax = fig.add_subplot(313)
rects = ax.bar( np.arange(0,366), pcnt, color='b', edgecolor='b')
ax.set_ylabel("Precip Records")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(0,366)
ax.grid(True)
ax.set_ylim(top=12)
ax.text(180,10, '* Only non-zeros counted')



fig.savefig("140731.png", dpi=100)
fig.savefig("140731_s.png", dpi=45)
#iemplot.makefeature("test")
