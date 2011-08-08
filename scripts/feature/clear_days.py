import mx.DateTime
import numpy as np
from pyIEM import iemdb 
i = iemdb.iemdb()
asos = i['asos']
coop = i['coop']

sts = mx.DateTime.DateTime(2001,1,1)
ets = mx.DateTime.DateTime(2002,1,1)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
total = np.zeros( (12,))
counts = np.zeros( (12,))
years = []
# Figure out the coldest high day
while now < ets:
  rs = coop.query("""
  SELECT day, high from alldata where sday = '%s' and stationid = 'ia2203' and year > 1972
  ORDER by high ASC LIMIT 1
  """ % (now.strftime("%m%d"),)).dictresult()
  high = rs[0]['high']
  day = mx.DateTime.strptime(rs[0]['day'], '%Y-%m-%d')
  # Get ASOS data
  rs = asos.query("""
  SELECT count(*), sum( case when skyc1 in ('BKN','OVC') or skyc2 in ('BKN','OVC') or skyc3 in ('BKN','OVC') then 1 else 0 end ) as clouds
  ,max(tmpf) as high from t%s WHERE station = 'DSM' and valid BETWEEN '%s 8:00' and '%s 18:00'
    """ % (day.strftime("%Y"), day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d"))).dictresult()
  if rs[0]['clouds'] is None:
      rs[0] = {'clouds': 1, 'count': 1, 'high': 'M'}
  print day, rs[0]['clouds'], rs[0]['count'], high, rs[0]['high']
  #data.append( float(rs[0]['clouds']) / float(rs[0]['count']) )
  #years.append( int(day.strftime("%j")) )
  total[ now.month - 1 ] += float(rs[0]['clouds']) / float(rs[0]['count'])
  counts[ now.month - 1 ] += 1.0
  now += interval

sts = mx.DateTime.DateTime(2001,1,1)
ets = mx.DateTime.DateTime(2002,1,1)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
total2 = np.zeros( (12,))
counts2 = np.zeros( (12,))
years = []
# Figure out the coldest high day
while now < ets:
  rs = coop.query("""
  SELECT day, high from alldata where sday = '%s' and stationid = 'ia2203' and year > 1972
  ORDER by high DESC LIMIT 1
  """ % (now.strftime("%m%d"),)).dictresult()
  high = rs[0]['high']
  day = mx.DateTime.strptime(rs[0]['day'], '%Y-%m-%d')
  # Get ASOS data
  rs = asos.query("""
  SELECT count(*), sum( case when skyc1 in ('BKN','OVC') or skyc2 in ('BKN','OVC') or skyc3 in ('BKN','OVC') then 1 else 0 end ) as clouds
  ,max(tmpf) as high from t%s WHERE station = 'DSM' and valid BETWEEN '%s 8:00' and '%s 18:00'
    """ % (day.strftime("%Y"), day.strftime("%Y-%m-%d"), day.strftime("%Y-%m-%d"))).dictresult()
  if rs[0]['clouds'] is None:
      rs[0] = {'clouds': 1, 'count': 1, 'high': 'M'}
  print day, rs[0]['clouds'], rs[0]['count'], high, rs[0]['high']
  #data.append( float(rs[0]['clouds']) / float(rs[0]['count']) )
  #years.append( int(day.strftime("%j")) )
  total2[ now.month - 1 ] += float(rs[0]['clouds']) / float(rs[0]['count'])
  counts2[ now.month - 1 ] += 1.0
  now += interval

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar( np.arange(12) - 0.4, total / counts * 100.0, width=0.4, facecolor='b', label='Coldest')
ax.bar( np.arange(12), total2 / counts2 * 100.0, width=0.4, facecolor='r', label='Warmest')
ax.set_xlim(-0.5,11.5)
ax.set_ylim(0,100)
ax.set_ylabel("Approximate Average Cloudiness [%]")
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xticks( np.arange(12))
ax.set_title("Des Moines 8 AM - 6 PM Cloudiness during\n days with the record high temperature [1973-2010]")
ax.grid(True)
ax.legend()

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')