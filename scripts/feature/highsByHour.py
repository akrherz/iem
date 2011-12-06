#!/mesonet/python/bin/python

import pg
asos = pg.connect('asos', 'iemdb', user='nobody')
import numpy, mx.DateTime

obs = numpy.zeros( (366,), 'f')

for yr in range(1933,2011):
  highs = {}
  rs = asos.query("SELECT date(valid) as d, max(round(tmpf::numeric,0)) as high from \
       t%s WHERE tmpf > -50 and tmpf < 120 and station = 'DSM' \
       GROUP by d" % (yr,)).dictresult()
  for k in range(len(rs)):
    highs[ rs[k]['d'] ] = rs[k]['high']

  # Okay, now we query the obs
  rs = asos.query("SELECT date(valid) as d, extract(hour from valid) as h, \
       max(round(tmpf::numeric,0)) as t from t%s WHERE \
       station = 'DSM' and tmpf > -50 and tmpf < 120 GROUP by d, h" % (yr,) ).dictresult()
  # Figure out the counts per day, in case of ties
  for q in range(len(rs)):
    if highs[ rs[q]['d'] ] == rs[q]['t'] and rs[q]['h'] == 0:
      ts = mx.DateTime.strptime(rs[q]['d'], '%Y-%m-%d')
      #print 'hit', ts, rs[q]['t']
      obs[ int(ts.strftime("%j")) - 1] += 1


import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(numpy.arange(0,366) - 0.5, obs / 78.0 * 100.0, ec='b', fc='b')
xticks = []
xticklabels = []
for i in range(0,366):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day == 1:
    xticks.append(i)
    xticklabels.append( ts.strftime("%b") )
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(-0.4,366)
ax.grid()
ax.set_title("Daytime High Occuring during Midnight Hour\nDes Moines [1933-2010]")
ax.set_ylabel("Frequency [%]")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')


