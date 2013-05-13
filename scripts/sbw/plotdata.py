import matplotlib.pyplot as plt
import numpy as np
import mx.DateTime

cnt = []
size = []
xlabels = []
xticks = []
i = 0
for line in open('data.tmp'):
  tokens = line.split(",")
  ts = mx.DateTime.strptime(tokens[0], '%Y-%m-%d %H:%M')
  if (ts.hour % 6 == 0 and ts.minute == 0) or i == 0:
    xticks.append( i )
    lbl = ts.strftime("%I %p")
    if ts.hour == 0 or i == 0:
      lbl = lbl +"\n"+ ts.strftime("%-d %b")
    xlabels.append( lbl )
  cnt.append( float(tokens[1]) )
  size.append( float(tokens[2]) )
  i += 1

cnt = np.array( cnt )
size = np.array( size )

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("NWS Tornado Warnings [26-28 Apr 2011]\nContinuous 3:10 PM 26 Apr - 8:45 AM 28 Apr CDT")
ax.bar( np.arange(0,len(cnt)), cnt, facecolor='pink', edgecolor='pink',
  label='Count')
ax.set_ylabel("Active Tornado Warnings", color='r')
ax.set_xlabel("Time (CST)")
for tl in ax.get_yticklabels():
    tl.set_color('r')
ax.grid()
ax2 = ax.twinx()
ax2.plot( np.arange(0,len(cnt)), size, color='blue', label='Area')

ax2.set_xlim(0, len(size)+10)
ax2.set_xticks( xticks )
ax2.set_xticklabels( xlabels )
#ax2.set_yticks( (145000, 270000, 380000, 410000, 690000))
#ax2.set_yticklabels ( ('IA', 'KS', 'MT', 'CA', 'TX') )
ax2.set_ylabel("Total Area in Warning [sq km]", color='b')
for tl in ax2.get_yticklabels():
    tl.set_color('b')
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
