import mx.DateTime
import numpy as np
import numpy.ma
from pyIEM import iemdb
i = iemdb.iemdb()
asos = i['asos']


clouds = numpy.ma.zeros( (6,2012-1972) )

for yr in range(1973,2011):
  # Extract obs
  rs = asos.query("""
  SELECT valid + '10 minutes'::interval as d, skyc1, skyl1, skyc2, skyl2, skyc3, skyl3, skyl4, skyc4 from
  t%s WHERE station = 'DSM' and valid BETWEEN '%s-07-04 17:49' and '%s-07-04 23:49'
  """ % (yr, yr, yr)).dictresult()
  for i in range(len(rs)):
    ts = mx.DateTime.strptime(rs[i]['d'][:16], '%Y-%m-%d %H:%M')
    hr = ts.hour - 18
    data = 0
    if rs[i]['skyc1'] in ['OVC','BKN']:
      data = rs[i]['skyl1']
    elif rs[i]['skyc2'] in ['OVC','BKN']:
      data = rs[i]['skyl2']
    elif rs[i]['skyc3'] ==  ['OVC','BKN']:
      data = rs[i]['skyl3']
    elif rs[i]['skyc4'] ==  ['OVC','BKN']:
      data = rs[i]['skyl4']
    elif rs[i]['skyc1'] in ['CLR','FEW','SCT']:
      data = 0
    clouds[hr,yr-1973] = data

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

clouds.mask = np.where( clouds == 0, True, False)

res = ax.imshow( clouds, aspect='auto', rasterized=True, interpolation='nearest')
fig.colorbar(res)


fig.savefig('test.png')
