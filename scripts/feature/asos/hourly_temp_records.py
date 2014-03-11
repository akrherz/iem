# Compute something on the hourly temperature records, climatology perhaps
import iemdb
import datetime
import numpy
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

acursor.execute("SET TIME ZONE 'GMT'")

# Extract the climatologies
data = {}
acursor.execute("""
select to_char(valid + '10 minutes'::interval, 'MMDDHH24') as mmddhh, 
max(tmpf), min(tmpf) from alldata where station = 'DSM' and 
tmpf between -50 and 120 
and (extract(minute from valid) between 50 and 59 
or extract(minute from valid) = 0) and valid < '2010-01-01' GROUP by mmddhh
""")
for row in acursor:
    data[row[0]] = {'min': row[2], 'max': row[1]}

icursor.execute("""
select to_char(valid + '10 minutes'::interval, 'MMDDHH24') as mmddhh, 
max(tmpf), min(tmpf) from current_log where station = 'DSM' and 
tmpf between -50 and 120 
and (extract(minute from valid) between 50 and 59 
or extract(minute from valid) = 0) and 
(valid + '10 minutes'::interval) >= '2010-11-10' and
valid < '2010-11-10 23:30' GROUP by mmddhh 
ORDER by mmddhh ASC
""")
obs = []
for row in icursor:
    obs.append( row[1] )
    
sts = mx.DateTime.DateTime(2010,11,10,6)
ets = mx.DateTime.DateTime(2010,11,11,6)
interval = mx.DateTime.RelativeDateTime(hours=1)
now= sts
mx = numpy.zeros( (24,), 'f')
mn = numpy.zeros( (24,), 'f')
i =0
while now < ets:
    lkp = "%s" % (now.strftime("%m%d%H"),)
    print lkp
    mx[i] = data[lkp]['max']
    mn[i] = data[lkp]['min']
    i += 1
    now += interval

import matplotlib.pyplot as plt

#print v


fig = plt.figure()
ax = fig.add_subplot(111)

rects = ax.bar( numpy.arange(24) - 0.4, mx-mn, facecolor='#eeeeee',
bottom=mn, zorder=2, label="Range")

ax.scatter( numpy.arange(len(obs)), obs, zorder=3, label="2010", marker='o'
			,color='b', edgecolor='k', s=30)

ax.set_xlim(-0.5,24)
ax.set_xticks( (0,3,6,9,12,15,18,21) )
ax.set_xticklabels( ('Mid', '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM', '9 PM') )
ax.set_xlabel("Time of Day")
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_title("10 Nov - Des Moines Hourly Temperature Range [1948-2009]")
ax.legend()
ax.grid(True)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
