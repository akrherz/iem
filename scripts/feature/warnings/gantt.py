import iemdb
import pytz
from pyiem.nws import vtec
import datetime
import matplotlib.dates as mdates

MOS = iemdb.connect('mos', bypass=True)
mcursor = MOS.cursor()
mcursor.execute("""SELECT ftime, tmp from t2013 where station = 'KCID'
  and model = 'GFS' and runtime = '2013-01-29 18:00' ORDER by ftime ASC""")
mvalid = []
mtmpf = []
for row in mcursor:
    mvalid.append( row[0] )
    mtmpf.append( row[1] )


IEM = iemdb.connect('asos', bypass=True)
icursor = IEM.cursor()
icursor.execute("""SELECT valid, tmpf from t2013 WHERE station = 'CID'
  and valid > '2013-01-25' ORDER by valid ASC""")
valid = []
tmpf = []
for row in icursor:
    valid.append( row[0] )
    tmpf.append( row[1] )

POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

pcursor.execute("""SELECT issue, expire, phenomena, significance, eventid
 from warnings_2013 where ugc in ('IAZ052', 'IAC113') 
 and issue > '2013-01-25' and significance != 'A' ORDER by issue ASC""")

labels = []
events = []

for row in pcursor:
    labels.append("%s\n%s" % ("\n".join(vtec._phenDict[row[2]].split()), vtec._sigDict[row[3]]))
    events.append( [ row[0], row[1] ] )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

i = 1
for l,e in zip(labels, events):
    print e[1], e[0]
    secs = (e[1]-e[0]).seconds
    ax.barh(i -0.4,secs / 86400.0 , left=e[0])
    i += 1

ax.set_yticklabels(labels)

ax2 = ax.twinx()
ax2.plot(valid, tmpf, label='Obs')
ax2.plot(mvalid, mtmpf, label='Forecast')
ax2.set_ylabel("Air Temperature $^{\circ}\mathrm{F}$")
ax.set_title("Cedar Rapids, IA / Linn County Recent Weather")
ax.set_xlabel("Warnings as of 5 AM 30 January 2013")
ax.set_yticks(range(1, len(labels)+1))
sts = datetime.datetime(2013,1,26)
sts = sts.replace(tzinfo=pytz.timezone("America/Chicago"))
ets = datetime.datetime(2013,2,1)
ets = ets.replace(tzinfo=pytz.timezone("America/Chicago"))
ax.set_xlim( sts, ets )
ax.xaxis.set_major_locator(
                               mdates.DayLocator(interval=1,
                                                 tz=pytz.timezone("America/Chicago"))
                               )
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d %b',
                                                  tz=pytz.timezone("America/Chicago")))
ax.grid(True)
ax2.legend(loc=4, ncol=2)
fig.tight_layout()
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')