import psycopg2
import datetime
import numpy as np
import pytz
import matplotlib.pyplot as plt
import matplotlib.font_manager

ASOS = psycopg2.connect(database='asos', host='localhost', user='nobody',
                        port=5555)
acursor = ASOS.cursor()

sts = datetime.datetime(2017, 1, 19, 8, 30)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))
ets = datetime.datetime(2017, 1, 19, 23, 0)
ets = ets.replace(tzinfo=pytz.timezone("UTC"))
tzname = 'America/Chicago'
station = 'BTR'

sz = int((ets - sts).days * 1440 + (ets - sts).seconds / 60.) + 1

prec = np.ones((sz,), 'f') * -1

acursor.execute("""
 SELECT valid, tmpf, dwpf, drct,
 sknt, pres1, gust_sknt, precip from t2017_1minute WHERE station = %s
 and valid >= %s and valid < %s
 ORDER by valid ASC
""", (station, sts, ets))
tot = 0
print("Found %s rows for station" % (acursor.rowcount,))
for row in acursor:
    offset = int((row[0] - sts).days * 1440 + (row[0] - sts).seconds / 60)
    tot += (row[7] or 0)
    prec[offset] = tot


# Now we need to fill in the holes
lastval = 0
for i in range(sz):
    if prec[i] > -1:
        lastval = prec[i]
    if prec[i] < 0:
        ts = sts + datetime.timedelta(minutes=i)
        print("Missing %s, assigning %s" % (ts, lastval))
        prec[i] = lastval

rate1 = np.zeros((sz,), 'f')
rate15 = np.zeros((sz,), 'f')
rate60 = np.zeros((sz,), 'f')
for i in range(1, sz):
    rate1[i] = (prec[i] - prec[i-1])*60.
for i in range(15, sz):
    rate15[i] = (prec[i] - prec[i-15])*4.
for i in range(60, sz):
    rate60[i] = (prec[i] - prec[i-60])

xticks = []
xlabels = []
lsts = sts.astimezone(pytz.timezone(tzname))
lets = ets.astimezone(pytz.timezone(tzname))
interval = datetime.timedelta(minutes=1)
now = lsts
i = 0
while now < lets:
    if now.minute == 0 and now.hour % 4 == 0:
        xticks.append(i)
        xlabels.append(now.strftime("%-I %p"))

    i += 1
    now += interval

prop = matplotlib.font_manager.FontProperties(size=12)

(fig, ax) = plt.subplots(1, 1)

ax.bar(np.arange(sz), rate1, fc='b', ec='b', label="Hourly Rate over 1min",
       zorder=1)
ax.plot(np.arange(sz), prec, color='k', label="Accumulation", lw=2, zorder=2)
ax.plot(np.arange(sz), rate15, color='tan', label="Hourly Rate over 15min",
        linewidth=3.5, zorder=3)
ax.plot(np.arange(sz), rate60, color='r', label="Actual Hourly Rate",
        lw=3.5, zorder=3)

# Find max rate
maxi = np.argmax(rate1)
maxwindow = 0
maxwindowi = 0
for i in range(maxi-10, maxi+1):
    if (prec[i+10] - prec[i]) > maxwindow:
        maxwindow = prec[i+10] - prec[i]
        maxwindowi = i

print("MaxI: %s, rate: %s, window: %s-%s" % (maxi, rate1[maxi], maxwindowi,
                                             maxwindowi+10))

x = 0.02
ax.text(x, 0.935, "Peak 10min Window", transform=ax.transAxes,
        bbox=dict(fc='white', ec='None'))
for i in range(maxwindowi+1, maxwindowi+11):
    ts = lsts + datetime.timedelta(minutes=i)
    ax.text(x, 0.88-(0.05*(i-maxwindowi-1)),
            "%s %.2f" % (ts.strftime("%-I:%M %p"), prec[i] - prec[i-1], ),
            transform=ax.transAxes, fontsize=10,
            bbox=dict(fc='white', ec='None'))

ax.set_xticks(xticks)
ax.set_ylabel("Precipitation [inch or inch/hour]")
ax.set_xticklabels(xlabels)
ax.grid(True)
ax.set_xlim(0, sz)
ax.legend(loc=(0.55, 0.7), prop=prop, ncol=1)
ax.set_ylim(0, 7)
ax.set_yticks(range(0, 8, 1))
ax.set_xlabel("19 January 2017 (%s)" % (tzname,))
ax.set_title(("19 January 2017 Baton Rouge, LA (KBTR)\n"
              "One Minute Rainfall, %.2f inches total plotted"
              ) % (prec[-1],))


fig.savefig('test.png')
