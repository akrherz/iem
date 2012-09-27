import iemdb, mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
  SELECT extract(doy from one.d), two.avg - one.avg from
  (SELECT date(valid) as d, avg(tmpf) from t2010 WHERE station = 'LWD' 
  GROUP by d) as one,
  (SELECT date(valid) as d, avg(tmpf) from t2010 WHERE station = 'CSQ' 
  GROUP by d) as two WHERE one.d = two.d ORDER by one.d ASC
  """)
times = []
vals = []
for row in acursor:
    times.append( row[0] )
    vals.append( row[1] )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(times, vals)
#ax.legend()
xticks = []
xticklabels = []
for i in range(0,366):
  ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
  if ts.day == 1:
    xticks.append(i)
    xticklabels.append( ts.strftime("%b") )
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(0,366)
ax.set_title("2011 Average Daily Temperature Difference\nAnkeny KIKV (AWOS) minus Des Moines KDSM (ASOS)")
ax.set_ylabel("Temperature Difference [F]")

ax.grid(True)
fig.savefig('test.png')