import iemdb
import re
import numpy
import numpy.ma
import scipy.stats
import mx.DateTime
postgis = iemdb.connect('postgis', bypass=True)
pcursor = postgis.cursor()

pcursor.execute("""
SELECT issue, report, x(ST_Centroid(geom)), y(ST_Centroid(geom)) from warnings where wfo in ('ARX','DVN','DMX','OAX','FSD') and 
significance = 'W' and gtype = 'P' and phenomena = 'SV' and issue > '2008-01-01' 
""")

SVRs = []

for row in pcursor:
  tokens = re.findall(r'TIME...MOT...LOC [0-9]{4}Z ([0-9]{1,3})DEG ([0-9]{1,3})KT', row[1])
  if len(tokens) == 0:
    print row[1]
    continue
  (dir, sknt) = tokens[0]
  if int(sknt) > 80:
    continue
  data = {'sknt': int(sknt), 'drct': int(dir), 'ts': mx.DateTime.strptime(row[0].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"),
          'x': row[2], 'y': row[3] }
  SVRs.append(data)

SVR_DRCT = []
TOR_DRCT = []
SVR_SKNT = []
TOR_SKNT = []

# Now go get TORs
pcursor.execute("""
SELECT issue, report, x(ST_Centroid(geom)), y(ST_Centroid(geom)) from warnings where wfo in ('ARX','DVN','DMX','OAX','FSD') and 
significance = 'W' and gtype = 'P' and phenomena = 'TO' and issue > '2008-01-01' 
""")
slower = 0
right = 0
for row in pcursor:
  tokens = re.findall(r'TIME...MOT...LOC [0-9]{4}Z ([0-9]{1,3})DEG ([0-9]{1,3})KT', row[1])
  if len(tokens) == 0:
    print row[1]
    continue
  (dir, sknt) = tokens[0]
  if int(sknt) > 80:
    continue
  ts =  mx.DateTime.strptime(row[0].strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
  x = row[2]
  y = row[3]
  sd = []
  ss = []
  # Lets go look for warnings to compare with!
  for svr in SVRs:
    deltaT = svr['ts'] - ts
    if deltaT.minutes < -60 or deltaT.minutes > 0:
      continue
    delta = ((x - svr['x']) ** 2 + (y - svr['y']) ** 2) ** .5
    if delta > 1.:
      continue
    # Hit!
    sd.append( svr['drct'] )
    ss.append( svr['sknt'] )

  if len(sd) > 0:
    asd = numpy.average( numpy.array(sd) )
    ass = numpy.average( numpy.array(ss) )
    SVR_DRCT.append( asd )
    SVR_SKNT.append( ass )
    TOR_DRCT.append( int(dir) )
    TOR_SKNT.append( int(sknt) )
    if int(sknt) < ass:
      slower += 1
    if int(dir) > asd:
      right += 1


TOR_DRCT = numpy.array( TOR_DRCT )
SVR_DRCT = numpy.array( SVR_DRCT )
TOR_SKNT = numpy.array( TOR_SKNT )
SVR_SKNT = numpy.array( SVR_SKNT )

print 'Drct', (scipy.stats.corrcoef(TOR_DRCT, SVR_DRCT)[0,1]) ** 2
print 'Sknt', (scipy.stats.corrcoef(TOR_SKNT, SVR_SKNT)[0,1]) ** 2

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)

ax.set_title("CONUS NWS Storm Motion Comparison 1 Jan 2008 - 5 Jul 2011\nSVR 0 to 60 minutes before TOR and within ~70 miles")

H2, xedges, yedges = numpy.histogram2d(TOR_DRCT, SVR_DRCT, bins=(36, 36),range=[[0,360],[0,360]])
H2 = numpy.ma.array(H2.transpose())
H2.mask = numpy.where( H2 < 1, True, False)
res = ax.imshow(H2,  aspect='auto', interpolation='nearest')
ax.grid(True)
fig.colorbar(res)

#ax.scatter( SVR_DRCT, TOR_DRCT )
ax.plot([0,36],[0,36], color='black')
ax.set_xlim(0,36)
ax.set_ylim(0,36)
ax.set_yticks( (0,9,18,27,36) )
ax.set_yticklabels( ('N','E','S','W','N') )
ax.set_xticks( (0,9,18,27,36) )
ax.set_xticklabels( ('N','E','S','W','N') )
ax.set_xlabel("Tornado Warn Direction, Right Turning: %.1f%%" % (right/float(len(TOR_DRCT))*100.0, ))
ax.set_ylabel("Svr T'storm Warn Direction")

ax2 = fig.add_subplot(212)
#ax2.scatter(SVR_SKNT, TOR_SKNT )
#ax2.set_xlim(0,80)
#ax2.set_ylim(0,80)
H, xedges, yedges = numpy.histogram2d(TOR_SKNT, SVR_SKNT, bins=(20, 20),range=[[0,80],[0,80]])
H = numpy.ma.array(H.transpose())
H.mask = numpy.where( H < 1, True, False)
res = ax2.imshow(H, aspect='auto', interpolation='nearest')
ax2.grid(True)
fig.colorbar(res)
ax2.plot([0,20],[0,20], color='black')
ax2.set_ylim(0,20)
ax2.set_xlim(0,20)
ax2.set_xticks( numpy.arange(0,20,5) )
ax2.set_xticklabels( numpy.arange(0,20,5) * 4 )
ax2.set_yticks( numpy.arange(0,20,5) )
ax2.set_yticklabels( numpy.arange(0,20,5) * 4 )
ax2.set_xlabel("Tornado Warn Speed [kts], Slower: %.1f%%" % (slower/float(len(TOR_SKNT))*100.0))
ax2.set_ylabel("Svr T'storm Warn Speed [kts]")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
