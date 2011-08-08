import iemdb 
COOP = iemdb.connect('asos', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select date(valid) as d, avg(sknt) from t2011 where station = 'AMW' and sknt >= 0 and valid > '2011-06-01' and valid < '2011-07-08' GROUP by d ORDER by d ASC
""")
sknt = []
for row in ccursor:
  sknt.append( row[1] * 1.15 )

import matplotlib.pyplot as plt
import numpy as np
import mx.DateTime
fig = plt.figure()
ax = fig.add_subplot(111)

ax.bar(np.arange(0,len(sknt)) - 0.4, sknt, facecolor='r')
ax.grid(True)
ax.set_ylabel("Average Wind Speed [mph]")
#ax.set_xlabel("Date since 1 June 2011")
ax.set_title("Ames Daily Average Wind Speed (1 Jun - 7 Jul 2011)")
ax.set_xlim(-0.4,len(sknt)-0.4)
xticks = []
xticklabels = []
for i in range(0,len(sknt)):
  ts = mx.DateTime.DateTime(2011,6,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day == 1:
    xticks.append(i)
    xticklabels.append( ts.strftime("%-d\n%b") )
  if ts.day % 3 == 0:
    xticks.append(i)
    xticklabels.append( ts.strftime("%-d") )
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
