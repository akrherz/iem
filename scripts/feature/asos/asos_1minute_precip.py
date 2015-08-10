import psycopg2
import datetime
import numpy as np
import pytz
import matplotlib.pyplot as plt
import matplotlib.font_manager

ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()

sts = datetime.datetime(2015, 8, 9, 7, 0)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))
ets = datetime.datetime(2015, 8, 9, 12, 0)
ets = ets.replace(tzinfo=pytz.timezone("UTC"))

sz = int((ets - sts).days * 1440 + (ets - sts).seconds / 60.) + 1

prec = np.ones((sz,), 'f') * -1

acursor.execute("""
 SELECT valid, tmpf, dwpf, drct,
 sknt, pres1, gust_sknt, precip from t2015_1minute WHERE station = 'AMW'
 and valid >= %s and valid < %s
 ORDER by valid ASC
""", (sts, ets))
tot = 0
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
lsts = sts.astimezone(pytz.timezone("America/Chicago"))
lets = ets.astimezone(pytz.timezone("America/Chicago"))
interval = datetime.timedelta(minutes=1)
now = lsts
i = 0
while now < lets:
    if now.minute == 0 and now.hour % 1 == 0:
        xticks.append(i)
        xlabels.append(now.strftime("%-I %p"))

    i += 1
    now += interval

print xticks

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

ax.text(0.05, 0.935, "Peak Minute Accums", transform=ax.transAxes,
        bbox=dict(fc='white', ec='None'))
for i in range(maxwindowi, maxwindowi+10):
    ts = lsts + datetime.timedelta(minutes=i)
    ax.text(0.05, 0.9-(0.035*(i-maxwindowi)),
            "%s %.2f" % (ts.strftime("%-I:%M %p"), prec[i] - prec[i-1], ),
            transform=ax.transAxes, bbox=dict(fc='white', ec='None'))

ax.set_xticks(xticks)
ax.set_ylabel("Precipitation [inch or inch/hour]")
ax.set_xticklabels(xlabels)
ax.grid(True)
ax.set_xlim(0, sz)
ax.legend(loc=1, prop=prop, ncol=1)
ax.set_ylim(0, int(np.max(rate1)+4))
ax.set_xlabel("9 Aug 2015 (Central Daylight Time)")
ax.set_title(("9 August 2015 Ames (KAMW)\n"
              "One Minute Rainfall %s inches total plotted") % (prec[-1],))


fig.savefig('test.png')
