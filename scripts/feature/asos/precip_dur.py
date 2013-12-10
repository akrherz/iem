
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import iemdb
import numpy
import datetime

x = []
y = []
x10 = []
y10 = []
dbconn = iemdb.connect('iem', bypass=True)
c = dbconn.cursor()
c.execute("SELECT phour, valid from hourly WHERE station = 'DSM' and phour > 0.005 ORDER by valid ASC")
running = 1
lts = None
for row in c:
  if lts is None:
    lts = row[1]

  if (row[1] - lts).seconds == 3600:
    running += 1
  else:
    if running > 15 and lts.month in (7,8):
      print running, lts
    if running > 9:
      x10.append( float(row[1].strftime("%j")) )
      y10.append( running )
    x.append( float(row[1].strftime("%j")) )
    y.append( running )
    running = 1
  lts = row[1]

c.close()
dbconn.close()

plt.subplot(111)

#heatmap, xedges, yedges = numpy.histogram2d(x, y, bins=50)
#extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

#plt.clf()
#plt.imshow(heatmap, extent=extent)


plt.hexbin(x,y, gridsize=(52,12), cmap=cm.jet_r)
ax = plt.gca()
ax.set_axis_bgcolor(plt.cm.jet_r(0)) 
ax.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
ax.set_xticklabels( ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec") )
ax.set_ylim(1,35)
ax.set_xlim(0,360)
ax.grid(True)
ax.scatter( x10, y10, color='white', marker="+")

ax.set_title("Des Moines Rainfall Duration\nConsec Hours with Precip (1973-2010)")
ax.set_ylabel("Hours")

#ax.bar( edges[:-1], bins , width=0.154, color='b', label="2010")
#ax.bar( edges[:-1] + 0.154, bins2 / 10.0, width=0.154, color='r', label="2000-2009")
#n, bins, patches = ax.hist( data, 25, normed=True)
#print bins
cb = plt.colorbar()
cb.set_label('occurrences')
plt.savefig("test.ps")
