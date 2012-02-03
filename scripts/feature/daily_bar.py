import iemdb 
import numpy as np
import datetime
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

cnts = np.zeros( (366,), 'f')
tots = np.zeros( (366,), 'f')
cnts30 = np.zeros( (366,), 'f')
tots30 = np.zeros( (366,), 'f')

for yr in range(2000,2012):
  acursor.execute("""
  select extract(doy from daily.d) as dd, 
  sum(case when (daily.max - minute.tmpf)  < 3 and (daily.max - daily.min) >= 15 then 1 else 0 end),
  sum(case when (daily.max - minute.tmpf)  < 3 and (daily.max - daily.min) >= 30 then 1 else 0 end)
   from (select date(valid) as d, tmpf from t%s_1minute 
   where station = 'DSM' and tmpf between -50 and 120) as minute, 
   (select date(valid) as d, max(tmpf), min(tmpf) from t%s_1minute where 
   station = 'DSM' and tmpf between -50 and 120 GROUP by d) as daily 
   WHERE daily.d = minute.d GROUP by dd ORDER by dd ASC;

  """ % (yr,yr))
  for row in acursor:
      if row[1] > 0:
          cnts[ int(row[0]) - 1] += 1
          tots[ int(row[0]) - 1] += row[1]
      if row[2] > 0:
          cnts30[ int(row[0]) - 1] += 1
          tots30[ int(row[0]) - 1] += row[2]

import matplotlib.pyplot as plt
import mx.DateTime
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(np.arange(0,366) - 0.5, tots / cnts / 60.0)
ax.plot(np.arange(0,366) - 0.5, tots30 / cnts30 / 60.0)

ax.grid(True)
ax.set_ylabel("High Temperature $^{\circ}\mathrm{F}$")
ax.set_title("Ames 95th Percentile High Temperature [1893-2011]")
ax.set_xlim(-0.4,366)
#ax.set_ylim(0,100)
xticks = []
xticklabels = []
for i in range(0,366):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day == 1:
    xticks.append(i)
    xticklabels.append( ts.strftime("%b") )
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)

#ax.annotate("50s in December are like\n100 degrees in July", xy=(340, 50),  
#  xycoords='data',
#                xytext=(-210, -40), textcoords='offset points',
#                bbox=dict(boxstyle="round", fc="0.8"),
#                arrowprops=dict(arrowstyle="->",
#                connectionstyle="angle3,angleA=-90,angleB=0"))

#ax.annotate("", xy=(200, 90),
#  xycoords='data',
#                xytext=(0, -80), textcoords='offset points',
#                bbox=dict(boxstyle="round", fc="0.8"),
#                arrowprops=dict(arrowstyle="->",
#                connectionstyle="angle3,angleA=-90,angleB=0"))



fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
