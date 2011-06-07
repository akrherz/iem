import iemdb
RWIS = iemdb.connect('rwis', bypass=True)
rcursor = RWIS.cursor()
import mx.DateTime

def timeX(valid):
  xticks = []
  xticklabels = []
  ts0 = mx.DateTime.DateTimeFromTicks(valid[0])
  day0 = ts0 + mx.DateTime.RelativeDateTime(hour=0,minute=0,second=0)
  ts1 = mx.DateTime.DateTimeFromTicks(valid[-1])
  day1 = ts1 + mx.DateTime.RelativeDateTime(days=1,hour=0,minute=0,second=0)
  interval = mx.DateTime.RelativeDateTime(hours=24)
  now = ts0
  while now <= ts1:
     xticks.append( int(now) )
     fmt = "%I %p"
     if now.hour == 0:
         fmt += "\n%d %b"
     fmt = "%d %b"
     xticklabels.append( now.strftime(fmt) )
     now += interval

  return xticks, xticklabels

rcursor.execute("""
  SELECT extract(epoch from valid), tfs0, tmpf from t2011 where station = 'RCTI4' and valid > '2011-05-12' ORDER by valid ASC
  """)
valid = []
obs = []
tmpf = []
for row in rcursor:
  valid.append( row[0] )
  obs.append( row[1] )
  tmpf.append( row[2] )

rcursor.execute("""
  SELECT extract(epoch from valid), s0temp, s1temp, s2temp, s3temp, s4temp, s5temp, s12temp from t2011_soil where station = 'RCTI4' and valid > '2011-05-12' ORDER by valid ASC
  """)
svalid = []
s0 = []
s1 = []
s2 = []
s3 = []
s4 = []
s5 = []
s6 = []
for row in rcursor:
  svalid.append( row[0] )
  s0.append( row[1] )
  s1.append( row[2] )
  s2.append( row[3] )
  s3.append( row[4] )
  s4.append( row[5] )
  s5.append( row[6] )
  s6.append( row[7] )


import matplotlib.pyplot as plt

xticks, xticklabels = timeX(valid)

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(valid, obs, label='Pavement')
ax.plot(valid, tmpf, label='Air', linestyle='-.')
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.grid(True)

ax.plot(svalid, s0, label='1 in')
ax.plot(svalid, s1, label='3 in')
#ax.plot(svalid, s2, label='6')
ax.plot(svalid, s3, label='9 in')
#ax.plot(svalid, s4, label='12')
ax.plot(svalid, s5, label='18 in')
ax.plot(svalid, s6, label='60 in', linestyle='--')
ax.legend(loc=9, ncol=3)
ax.set_title("Cantril, Iowa RWIS Timeseries\nPavement, Air, and Sub Surface Temperatures")
ax.set_ylabel('Temperature $^{\circ}\mathrm{F}$')
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
