import iemdb, datetime, iemtz
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

sts = datetime.datetime(2012,11,19,0, tzinfo=iemtz.Central)
ets = datetime.datetime(2012,11,21,6,1, tzinfo=iemtz.Central)
dt = datetime.timedelta(hours=6)
now = sts
xticks = []
xticklabels = []
while now < ets:
  xticks.append( now )
  fmt = '%-I %p'
  if now.hour == 0:
      fmt = '%-I %p\n%d %b'
  xticklabels.append( now.strftime(fmt) )
  now += dt

def get2(station, param):
  times = []
  vals = []
  acursor.execute("""
  SELECT valid, %s from t2012 WHERE 
  station = '%s' and valid >= '2012-11-19 00:00' and 
  valid < '2012-11-21 8:00' ORDER by valid ASC
  """ % (param, station))
  for row in acursor:
    times.append( row[0])
    vals.append( row[1] )
  return times, vals


def get(station, network):
  times = []
  vals = []
  icursor.execute("""
  SELECT valid, tmpf from current_log c JOIN stations s on (s.iemid = c.iemid)
  and s.network = '%s' and s.id = '%s' and valid >= '2012-11-19 00:00' and 
  valid < '2012-11-21 12:00' ORDER by valid ASC
  """ % (network, station))
  for row in icursor:
    times.append( row[0])
    vals.append( row[1] )
  return times, vals

import iemplot
import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)


fig = plt.figure()
ax = fig.add_subplot(111)

#times, vals = get2("AMW")
#ax.plot(times, vals, label="Ames Airport (1min) %.0f" % (min(vals),))

times, vals = get2("ALO", 'tmpf')
ax.plot(times, vals, label="Waterloo")
#mn = min(vals)
#mx = max(vals)
#z = [mn,mx]
#for x,y in zip(times, vals):
#    if y in z:
#        delta = 1
#        if y < 20:
#            delta = -3
#        ax.text(x, y + delta, "%.0f$^{\circ}\mathrm{F}$, @%s" % (y,
#                                                    x.strftime("%-I:%M %p")),
#                ha='center')
#        z.remove(y)

times, vals = get2("DSM", 'tmpf')
ax.plot(times, vals, label="Des Moines")
#times, vals = get("SBSI4", "KCCI")
#ax.plot(times, vals, label="Bussey School")
#times, vals = get("SPEI4", "KCCI")
#ax.plot(times, vals, label="Pella School")
#times, vals = get("GGI", "AWOS")
#ax.plot(times, vals, label="Grinnell")

#times, vals = get("OT0002", "OT")
#ax.plot(times, vals, label="ISU Agronomy Hall %.0f" % (min(vals),))
#times, vals = get("OT0009", "OT")
#ax.plot(times, vals, label="Beliot Center %.0f" % (min(vals),))
#times, vals = get("SAMI4", "KCCI")
#ax.plot(times, vals, label="St Cecilia SchoolNet %.0f" % (min(vals),))

#ax.plot([xticks[2],xticks[4]], [28,28], label="Ames NWS COOP 28")
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.grid(True)
ax.legend(loc=2, ncol=2, prop=prop)
#ax.set_ylim(35,75)
ax.set_title("12-14 October 2012 Waterloo Dew Point Timeseries")
ax.set_ylabel("Dew Point Temperature $^{\circ}\mathrm{F}$")

fig.savefig('test.ps')
iemplot.makefeature('test')
