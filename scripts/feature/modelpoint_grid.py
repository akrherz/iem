import iemdb
import numpy.ma
import datetime
import iemtz

MOS = iemdb.connect('mos', bypass=True)
mcursor = MOS.cursor()

# GFS has 8 days worth of data
# NAM has 3.5 days
PLOTDAYS = 3
sts = datetime.datetime(2012,4,8,0, tzinfo=iemtz.Central)
#___________________________
# No more custom
MODELDAYS = PLOTDAYS+8-2
msts = sts - datetime.timedelta(days=8)
ets = sts + datetime.timedelta(days=PLOTDAYS)

qpf = numpy.ma.zeros( (MODELDAYS*4, PLOTDAYS*8), numpy.float)
qpf[:] = -1.



xlabels = []
xticks = range(-1,PLOTDAYS*8,4)
for i in range(-1,PLOTDAYS*8,4):
    ts = sts + datetime.timedelta(hours=((i+1)*3))
    fmt = "%-I %p"
    if ts.hour == 0:
        fmt += "\n%d %b"
    xlabels.append( ts.strftime(fmt))

ylabels = []
yticks = range(0,MODELDAYS*4,4)
for i in range(0,MODELDAYS*4,4):
    ts = msts + datetime.timedelta(hours=(i*6))
    fmt = "%d %b"
    ylabels.append( ts.strftime(fmt))


mcursor.execute("""
select runtime, ftime, precip from model_gridpoint_2012 
where station = 'KSUX' and ftime > %s and ftime <= %s and model = 'GFS'
""", (sts, ets))

for row in mcursor:
    runtime = row[0]
    ftime = row[1]
    precip = row[2]
    y = ((ftime - sts).days * 86400. + (ftime - sts).seconds) / 10800.
    x = ((runtime - msts).days * 86400. + (runtime - msts).seconds) / 21600.

    #print runtime, ftime, x, y, precip
    if precip is not None:
        qpf[int(x),int(y)-1] = precip / 25.4

# Darn GFS 3hr precip is actually a 6 hr on the 6th hour
for y in range(1,PLOTDAYS*8,2):
    for x in range(0,MODELDAYS*4):
        if qpf[x,y] > 0:
            qpf[x,y] -= qpf[x,y-1]

qpf.mask = numpy.where( qpf < 0, True, False)
#print qpf
import matplotlib.pyplot as plt
import matplotlib.mpl as mpl

bounds = [0.01,0.02,0.05,0.07,0.10,0.15,0.20,0.25,0.30,0.40,0.50]
cmap = mpl.cm.jet
#cmap.set_over('0.25')
cmap.set_under('#F9CCCC')
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)



fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( qpf, aspect='auto', rasterized=True,
        interpolation='nearest', cmap=cmap, norm=norm)
ax.set_ylim(0,MODELDAYS*4)
fig.colorbar( res )
ax.grid(True)

ax.set_title("GFS Grid Point Forecast for Ames\n3 Hour Total Precipitation [inch]")

ax.set_xticks( numpy.array(xticks) + 0.5 )
ax.set_xticklabels( xlabels )
ax.set_yticks( yticks )
ax.set_yticklabels( ylabels )

ax.set_xlabel('Forecast Date')
ax.set_ylabel('Model Run')
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
