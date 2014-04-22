import iemdb
import numpy.ma
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

data = numpy.ma.zeros( (24,54), 'f')

acursor.execute("""
select distinct extract(doy from valid), extract(year from valid), 
 extract(hour from valid), extract(week from valid) from alldata where presentwx ~* 'TS' and station = 'DSM'""")

doy = []
hr = []
miny = 2012
for row in acursor:
  data[ row[2], row[3] ] += 1
  if row[1] < miny:
    miny = row[1]

print miny

data.mask = numpy.where( data == 0, True, False)

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( data, aspect='auto', rasterized=True, interpolation='nearest')
fig.colorbar( res )
ax.set_ylim(-0.5,23.5)
ax.set_yticks( (0,4,8,12,16,20))
ax.set_yticklabels( ('Mid','4 AM','8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xticks( numpy.arange(0,55,7) )
ax.set_xticklabels( ('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15', 'Sep 2', 'Oct 21', 'Dec 9'))
ax.set_title("Des Moines Thunder Reports [%.0f - 2011]\nby hour and by week of the year" % (miny,))
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
