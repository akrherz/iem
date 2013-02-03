import iemdb
import iemplot
import datetime

MOS = iemdb.connect('mos', bypass=True)
mcursor = MOS.cursor()
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

station = 'AMW'

mos = []
obs = []
times = []

# Extract MOS forecasts
mcursor.execute("""SELECT ftime, tmp from t2012
    WHERE station = 'KDSM' and ftime - runtime = '24 hours'::interval 
    and model = 'GFS' ORDER by ftime ASC 
""")
for row in mcursor:
    acursor.execute("""SELECT tmpf from t2012
    WHERE station = 'DSM' and valid BETWEEN %s::timestamp - '10 minutes'::interval
    and %s""", (row[0],row[0]))
    row2 = acursor.fetchone()
    if row2 is None:
        continue
    mos.append( row[1] )
    obs.append( row2[0] )
    times.append( row[0] )
    
import matplotlib.pyplot as plt
import numpy

obs = numpy.array(obs)
mos = numpy.array(mos)

fig = plt.figure()
ax = fig.add_subplot(111)


bars = ax.bar(times, obs - mos, fc='r', ec='r')
for bar in bars:
    if bar.get_y() < 0:
        bar.set_edgecolor('b')
        bar.set_facecolor('b')

ax.grid(True)
ax.set_ylabel("Observation minus Model $^{\circ}\mathrm{F}$")
xticks = []
xticklabels = []
for i in range(1,11):
    xticks.append( datetime.datetime(2012,i,1) )
    xticklabels.append( datetime.datetime(2012,i,1).strftime("%b"))

ax.set_title("GFS Model Output Statistics for Des Moines KDSM 2012\nDifference in forecast hour 24 Air Temperature")
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(min(xticks), max(xticks))

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
