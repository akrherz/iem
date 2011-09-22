import matplotlib.pyplot as plt
import mx.DateTime

x = []
y = []
for line in open('hits.txt'):
    tokens = line.split(":")
    ts = mx.DateTime.strptime(tokens[0], '%d %B %Y')
    x.append( ts )
    y.append( int(tokens[1])  )

fig = plt.figure()
ax = fig.add_subplot(111)

ax.semilogy(x, y)
#ax.set_xlim( x[0].ticks(), x[-1].ticks() )
xticks = []
xticklabels = []
ts0 = mx.DateTime.DateTime(2001,1,1)
ts1 = mx.DateTime.DateTime(2012,1,2)
interval = mx.DateTime.RelativeDateTime(days=1)
now = ts0
while now < ts1:
    if  (now.day == 1 and now.month == 1):
        xticks.append( now )
        xticklabels.append( now.strftime("%Y"))
    now += interval
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_ylabel("Maximum Daily Web Hits")
ax.set_title("IEM Website Hits Milestones [17 Jun 2001-2011]")
ax.grid(True)
fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')
