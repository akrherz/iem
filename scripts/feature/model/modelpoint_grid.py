import psycopg2
import numpy.ma
import datetime
import pytz

MOS = psycopg2.connect(database='mos', host='iemdb', user='nobody')
mcursor = MOS.cursor()
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

# GFS has 8 days worth of data
# NAM has 3.5 days
PLOTDAYS = 7
# TODO: this is a bug here
sts = datetime.datetime(2014, 9, 20, 0,
                        tzinfo=pytz.timezone("America/Chicago"))
#
# No more custom
MODELDAYS = PLOTDAYS+ 6
msts = sts - datetime.timedelta(days=8)
ets = sts + datetime.timedelta(days=PLOTDAYS)

qpf = numpy.ma.zeros( (MODELDAYS*4+2, PLOTDAYS*8), numpy.float)
qpf[:] = -1.



xaxis = []
xlabels = []
xticks = range(-1,PLOTDAYS*8, 4)
for i in range(-1,PLOTDAYS*8):
    ts = sts + datetime.timedelta(hours=((i+1)*3))
    xaxis.append( ts )
    fmt = "Noon"
    if ts.hour == 0:
        fmt = "Mid\n%d %b"
    if ts.hour in [0,12]:
        xlabels.append( ts.strftime(fmt))

ylabels = []
yticks = range(0,MODELDAYS*4,4)
for i in range(0,MODELDAYS*4,4):
    ts = msts + datetime.timedelta(hours=(i*6))
    fmt = "%d %b"
    ylabels.append( ts.strftime(fmt))
    

obs = numpy.zeros( (PLOTDAYS*8), numpy.float )
for i,x in enumerate(xaxis[:-1]):
    icursor.execute("""SELECT sum(phour) from hourly_2014 where
     station = 'AMW' and valid >= %s and valid < %s """, (x,
                            x + datetime.timedelta(hours=3)))
    row = icursor.fetchone()
    obs[i] = row[0] 
    print i, x, row[0]
qpf[-1,:] = obs



mcursor.execute("""
select runtime, ftime, precip from model_gridpoint_2014
where station = 'KAMW' and ftime > %s and ftime <= %s and model = 'GFS'
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
            nv = qpf[x,y] - qpf[x,y-1]
            if nv < 0:
                print x,y,nv
                qpf[x,y] = 0.001
            else:
                qpf[x,y] = nv

qpf.mask = numpy.where( qpf < 0, True, False)
print qpf[-1,:]
import matplotlib.pyplot as plt
import matplotlib.mpl as mpl
import matplotlib.dates as mdates

bounds = [0.01,0.02,0.05,0.07,0.10,0.15,0.20,0.25,0.30,0.40,0.50]
cmap = mpl.cm.jet
#cmap.set_over('0.25')
cmap.set_under('#F9CCCC')
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( qpf, aspect='auto', rasterized=True,
        interpolation='nearest', cmap=cmap, norm=norm)
ax.set_ylim(0,MODELDAYS*4+2)
fig.colorbar( res )
ax.grid(True)

ax.set_title("GFS Grid Point Forecast for Ames\n3 Hour Total Precipitation [inch]")

ax.set_xticks( numpy.array(xticks) + 0.5 )
ax.set_xticklabels( xlabels , fontsize=8)
ax.set_yticks( yticks )
ax.set_yticklabels( ylabels )
ax.set_xlabel('Forecast Date')
ax.set_ylabel('Model Run')

ax.text(-0.01, 1, "Obs->", ha='right', va='top', transform=ax.transAxes)

fig.savefig('test.png')
