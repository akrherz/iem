import psycopg2
import numpy.ma
import datetime
import pytz
from pyiem.datatypes import distance
import matplotlib.pyplot as plt
import matplotlib.colors as mpcolors

MOS = psycopg2.connect(database='mos', host='localhost', port=5555,
                       user='nobody')
mcursor = MOS.cursor()
IEM = psycopg2.connect(database='iem', host='localhost', port=5555,
                       user='nobody')
icursor = IEM.cursor()

# GFS has 8 days worth of data
# NAM has 3.5 days
PLOTDAYS = 7
sts = datetime.datetime(2016, 7, 5, 18)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))
sts = sts.astimezone(pytz.timezone("America/Chicago"))
#
# No more custom
MODELDAYS = PLOTDAYS + 6
msts = sts - datetime.timedelta(days=8)
ets = sts + datetime.timedelta(days=PLOTDAYS)

ymax = MODELDAYS * 4 + 2
xmax = PLOTDAYS * 8
qpf = numpy.ma.zeros((ymax, xmax), numpy.float)
qpf[:] = -1.

xaxis = []
xlabels = []
xticks = range(-1, PLOTDAYS * 8, 4)
for i in range(-1, PLOTDAYS * 8):
    ts = sts + datetime.timedelta(hours=((i+1)*3))
    xaxis.append(ts)
    fmt = "1 PM"
    if ts.hour == 1:
        fmt = "1 AM\n%d %b"
    if ts.hour in [1, 13]:
        xlabels.append(ts.strftime(fmt))

ylabels = []
yticks = range(0, MODELDAYS*4, 4)
for i in range(0, MODELDAYS*4, 4):
    ts = msts + datetime.timedelta(hours=(i*6))
    fmt = "%d %b"
    ylabels.append(ts.strftime(fmt))


obs = numpy.zeros((PLOTDAYS*8), numpy.float)
for i, x in enumerate(xaxis[:-1]):
    icursor.execute("""SELECT sum(phour) from hourly_2016 where
     station = 'AMW' and valid >= %s and valid < %s
     """, (x, x + datetime.timedelta(hours=3)))
    row = icursor.fetchone()
    obs[i] = row[0]
    print("Obs: i=%s x=%s val=%s" % (i, x, row[0]))
qpf[-1, :] = obs

mcursor.execute("""
 select runtime, ftime, precip from model_gridpoint_2016
 where station = 'KAMW' and ftime > %s and ftime <= %s and model = 'GFS'
 and (ftime - runtime) < '10 days'::interval
 ORDER by ftime ASC
""", (sts, ets))

for row in mcursor:
    runtime = row[0]
    ftime = row[1]
    precip = row[2]
    x = int((ftime - sts).total_seconds() / 10800.) - 1
    y = int((runtime - msts).total_seconds() / 21600.)

    if y == 0:
        print runtime, ftime, x, y, (ftime - sts).seconds, precip
    if precip is not None:
        if x < xmax and y < (ymax - 2) and x >= 0 and y >= 0:
            qpf[y, x] = distance(precip, 'MM').value('IN')

# Darn GFS 3hr precip is actually a 6 hr on the 6th hour
for x in range(1, PLOTDAYS * 8, 2):
    for y in range(0, MODELDAYS*4):
        if qpf[y, x] > 0:
            nv = qpf[y, x] - qpf[y, x-1]
            if nv < 0:
                qpf[y, x] = 0.001
            else:
                qpf[y, x] = nv
print qpf[43, :]

qpf.mask = numpy.where(qpf < 0, True, False)
print qpf[-1, :]

bounds = [0.01, 0.02, 0.05, 0.07, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
cmap = plt.get_cmap('jet')
cmap.set_under('#F9CCCC')
norm = mpcolors.BoundaryNorm(bounds, cmap.N)

fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow(qpf, aspect='auto', rasterized=True,
                interpolation='nearest', cmap=cmap, norm=norm)
ax.set_ylim(0, MODELDAYS * 4 + 2)
fig.colorbar(res)
ax.grid(True)

ax.set_title(("GFS Grid Point Forecast for Ames\n"
              "3 Hour Total Precipitation [inch]"))

ax.set_xticks(numpy.array(xticks) + 0.5)
ax.set_xticklabels(xlabels, fontsize=8)
ax.set_yticks(yticks)
ax.set_yticklabels(ylabels)
ax.set_xlabel('Forecast Date')
ax.set_ylabel('Model Run')

ax.text(-0.01, 1, "Obs->", ha='right', va='top', transform=ax.transAxes)

fig.savefig('test.png')
