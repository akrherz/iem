
import mx.DateTime

import numpy
import iemdb
postgis = iemdb.connect("postgis", bypass=False)
asos = iemdb.connect("asos", bypass=True)

# Query all btids, max(time) within box at cat2 and greater
# N: 29.5
# W: -97
# S: 23.5
# E: -82.5
data = numpy.zeros( (168*2+2), 'f')
cnts = numpy.zeros( (168*2+2), 'f')
maxv = numpy.zeros( (168*2+2), 'f')
minv = numpy.zeros( (168*2+2), 'f')
minv[:] = 1000.0

acursor = asos.cursor()
pcursor = postgis.cursor()
pcursor.execute("""SELECT btid, max(valid) from atl_hurricanes WHERE
    the_geom && ST_SetSRID(ST_MakeBox2D(ST_Point(-97.0, 23.5),
	ST_Point(-82.5, 29.5)),4326) and valid > '1950-01-01' and 
    cat in ('H1','H2','H3','H4','H5') and extract(month from valid) = 9 GROUP by btid""")
for row in pcursor:
  ts = row[1]
  acursor.execute("""SELECT valid, dwpf from t%s WHERE station = 'DSM' and
   valid BETWEEN '%s'::timestamptz - '7 days'::interval and '%s'::timestamptz + '7 days'::interval and dwpf >= 0 ORDER by valid ASC
   """ % (ts.year, ts.strftime("%Y-%m-%d %H:00"), 
          ts.strftime("%Y-%m-%d %H:00")))
  for row2 in acursor:
    hr = ((row2[0] - ts).days * 86400. + (row2[0] - ts).seconds) / 3600
    offset = 168 + int(hr)
    v = row2[1]
    if v > maxv[offset]:
       maxv[offset] = v
    if v < minv[offset]:
       minv[offset] = v
    data[offset] += row2[1]
    cnts[offset] += 1

vals = []
for h in range(168*2+1):
  print "%s,%.2f" % (h-168, data[h] / cnts[h] )
  vals.append( data[h] / cnts[h] )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(numpy.arange(168*2+2), maxv, color='r')
ax.plot(numpy.arange(168*2+2), minv, color='b')
ax.plot(numpy.arange(168*2+1), vals, color='g')
plt.savefig('test.png')
