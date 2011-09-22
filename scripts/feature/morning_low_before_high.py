import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor2 = ASOS.cursor()

# Extract 100 degree obs
acursor.execute("""
 SELECT distinct date(valid), valid, tmpf from alldata WHERE station = 'DSM'
and tmpf >= 100 and tmpf < 126 ORDER by valid ASC
""")
jdays = []
obtimes = []
obdays = []
jlows = []
ldate = None
for row in acursor:
    d = row[0]
    valid = row[1]
    if d != ldate:
        acursor2.execute("""
        SELECT min(tmpf) from t%s WHERE station = 'DSM' and valid BETWEEN
        '%s 00:00' and '%s 12:00' and tmpf > -50
        """ % (valid.year, d, d))
        low = acursor2.fetchone()[0]
        jlows.append(low)
        jdays.append(int(valid.strftime("%j")))
    ldate = d
    obdays.append(int(valid.strftime("%j")))
    obtimes.append( valid.hour * 60 + valid.minute )

import mx.DateTime
xticks = []
xticklabels = []
for i in range(min(obdays)-5,max(obdays)+5):
    ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
    if ts.day == 1 or ts.day == 15:
        xticks.append( i )
        xticklabels.append( ts.strftime("%b %-d"))

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_title("Des Moines Days of 100+ Degree Temperatures [1948-2010]")
ax.scatter(jdays, jlows)
ax.set_xlim(min(obdays)-5,max(obdays)+5)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.grid(True)
ax.set_ylabel("Morning Low Temperature")

yticks = []
yticklabels = []
for i in range(750,1200):
    ts = mx.DateTime.DateTime(2000,1,1,0,0) + mx.DateTime.RelativeDateTime(minutes=i)
    if ts.minute == 0:
        yticks.append( i)
        yticklabels.append( ts.strftime("%I %p"))

ax2 = fig.add_subplot(212)
ax2.scatter(obdays, obtimes)
ax2.set_xlim(min(obdays)-5,max(obdays)+5)
ax2.set_xticks(xticks)
ax2.set_xticklabels(xticklabels)
ax2.set_yticks(yticks)
ax2.set_yticklabels(yticklabels)
ax2.set_ylabel("Time of 100+ Degree Obs")
ax2.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
    