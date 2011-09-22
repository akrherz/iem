import iemdb
import re
import numpy
import numpy.ma
postgis = iemdb.connect('postgis', bypass=True)
pcursor = postgis.cursor()

jday = []
drct = []
sknts = []

pcursor.execute("""
SELECT issue, report from warnings where wfo in ('FSD','DMX','DVN','OAX','ARX') and
significance = 'W' and gtype = 'P' and phenomena = 'SV' and issue > '2008-01-01'
""")

for row in pcursor:
  tokens = re.findall(r'TIME...MOT...LOC [0-9]{4}Z ([0-9]{1,3})DEG ([0-9]{1,3})KT', row[1])
  if len(tokens) == 0:
    print row[1]
  (dir, sknt) = tokens[0]
  if int(sknt) > 80:
    continue
  jday.append( int(row[0].strftime("%j")) )
  drct.append( int(dir) )
  sknts.append( int(sknt) )

import matplotlib.pyplot as plt

H, xedges, yedges = numpy.histogram2d(jday, drct, bins=(53, 36),range=[[0,366],[0,360]])
H = numpy.ma.array(H.transpose())
H.mask = numpy.where( H < 1, True, False)

weight = numpy.zeros( (36,53), 'f')
for i in range(36):
  weight[i,:] = (i+1) * 10


fig = plt.figure()
ax = fig.add_subplot(211)

extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
print extent
print numpy.shape(H)
ax.set_title("1 Jan 2008 - 5 Jul 2011 NWS Storm Motion\nfor SVR T'storm warnings from Iowa WFOs")
res = ax.imshow(H,  extent=extent, aspect='auto', interpolation='nearest')
ax.set_ylim(0,360)
ax.set_yticks( (0,90,180,270,360) )
ax.set_yticklabels( ('N','E','S','W','N') )
fig.colorbar(res)
ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_ylabel("Storm Motion (from)")
ax.grid(True)

#fit = numpy.ma.average(H * weight, axis=0) / numpy.ma.sum( H, axis=0)
#print fit
#ax.plot( numpy.arange(0,366,7), fit  )


ax2 = fig.add_subplot(212)
#ax2.scatter(drct, sknts)
H2, xedges, yedges = numpy.histogram2d(drct, sknts, bins=(36, 20),range=[[0,360],[0,80]])
H2 = numpy.ma.array(H2.transpose())
H2.mask = numpy.where( H2 < 1, True, False)
extent2 = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
print extent2
print numpy.shape(H2)
res = ax2.imshow(H2,  aspect='auto', interpolation='nearest')
ax2.set_xlim(-0.5,35.5)
ax2.set_xticks( (0,9.,18.,27.,36.) )
ax2.set_xticklabels( ('N','E','S','W','N') )
ax2.set_ylim(-0.5,19.5)
ax2.set_yticks( numpy.arange(0,20,4) )
ax2.set_yticklabels( numpy.arange(0,20,4) * 4 )
ax2.set_xlabel("Storm Motion (from)")
ax2.set_ylabel("Storm Speed [kts]")
ax2.grid(True)
fig.colorbar(res)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
