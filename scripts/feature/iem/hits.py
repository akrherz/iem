import matplotlib.pyplot as plt
import datetime

x = []
y = []
for line in open('hits.txt'):
    tokens = line.split(":")
    ts = datetime.datetime.strptime(tokens[0], '%d %b %Y')
    x.append(ts)
    y.append(int(tokens[1]))

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)

ax.semilogy(x, y, lw=3)
# ax.set_xlim( x[0].ticks(), x[-1].ticks() )
xticks = []
xticklabels = []
ts0 = datetime.datetime(2001, 1, 1)
ts1 = datetime.datetime(2018, 1, 2)
interval = datetime.timedelta(days=1)
now = ts0
while now < ts1:
    if now.day == 1 and now.month == 1:
        xticks.append(now)
        xticklabels.append(now.strftime("%Y"))
    now += interval
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels, fontsize=20, rotation=90)
ax.set_xlabel("Year", fontsize=20)
ax.set_ylabel("Maximum Daily Web Requests", fontsize=20)
ax.set_title("IEM Web Requests Milestones [17 Jun 2001-2017]", fontsize=18)
ax.grid(True)
plt.setp(ax.get_yticklabels(), fontsize=20)
fig.tight_layout()
fig.savefig('test.png')
