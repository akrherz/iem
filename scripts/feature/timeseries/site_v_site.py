import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
SELECT sux.tmpf, brl.tmpf, sux.ts from
  (SELECT valid  as ts, tmpf from t2013 
  where station = 'SUX' and tmpf is not null
  and valid > '2013-03-01') as sux, 
  (SELECT valid  as ts, tmpf from t2013 
  where station = 'BRL' and tmpf is not null
  and valid > '2013-03-01') as brl

WHERE brl.ts = (sux.ts + '1 minutes'::interval) ORDER by sux.ts ASC
""")

sux = []
brl = []
valid = []
for row in acursor:
    valid.append( row[2] )
    sux.append( row[0] )
    brl.append( row[1] )

print sux[-10:], brl[-10:], valid[-10:]

acursor.execute("""
SELECT max(brl.tmpf - sux.tmpf), extract(year from sux.ts) as yr,
  min(brl.tmpf - sux.tmpf) from
  (SELECT valid  as ts, tmpf from alldata 
  where station = 'SUX' and tmpf is not null
  and valid > '1900-03-01') as sux, 
  (SELECT valid  as ts, tmpf from alldata 
  where station = 'BRL' and tmpf is not null
  and valid > '1900-03-01'
  and extract(month from valid) = 5 
  and extract(year from valid) != 1997 ) as brl

WHERE to_char(brl.ts + '10 minutes'::interval, 'YYYYMMDDHH24') = 
      to_char(sux.ts + '10 minutes'::interval, 'YYYYMMDDHH24')
      GROUP by yr ORDER by yr ASC
""")
years = []
maxes = []
mins = []
for row in acursor:
    years.append( row[1] )
    maxes.append( row[0] )
    mins.append( row[2] )

print years
print maxes

import numpy
sux = numpy.array(sux)
brl = numpy.array(brl)
years = numpy.array(years)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(2,1)

ax[0].plot(valid, brl - sux)
ax[0].set_title("Burlington vs Sioux City Temperature")
ax[0].set_ylabel("Temperature Difference $^{\circ}\mathrm{F}$")
ax[0].grid(True)
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%-d %b\n%Y'))

ax[1].bar(years - 0.4, maxes, ec='r', fc='r')
ax[1].set_xlim(1945,2014)
ax[1].set_ylabel("Largest May Difference $^{\circ}\mathrm{F}$")
ax[1].grid(True)
ax[1].set_xlabel("* 2013 just includes 1 May")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')