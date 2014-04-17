import mx.DateTime
import numpy as np
import pg
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

asos = pg.connect("asos", 'iemdb', user='nobody')

data = []

for yr in range(1973,2013):
# Get ASOS data
  rs = asos.query("""
  SELECT date(valid) as d, count(*), 
    sum( case when skyc1 in ('BKN','OVC') 
      or skyc2 in ('BKN','OVC') or skyc3 in ('BKN','OVC') then 1 else 0 end ) as clouds
   from t%s WHERE station = 'DSM' and valid < '%s-03-09'
  and extract(hour from valid) between 10 and 14 GROUP by d
    """ % (yr,yr)).dictresult()
  cnt = 0
  for row in rs:
    if row['clouds'] * 2 < row['count']:
        cnt += 1
  data.append( cnt )

#data[1998-1973] = 40

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

#ax.plot( np.arange(366), clear, label='Coldest')
ax.bar( np.arange(1973,2013)-0.4, data )
#ax.plot( np.arange(365), smooth(both_abovenormal[:365] / abovenormal[:365],7, 'hamming') * 100., label='Both')
#ax.set_xlabel("Des Moines 8AM-6PM [1973-2011]")
ax.set_ylabel("Days")
ax.set_title("Des Moines Mostly Clear @ Noon [1973-2012]\n1 Jan - 8 Mar (reported clouds were mostly not overcast nor broken)")
ax.grid(True)
#ax.set_ylim(20,56)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
