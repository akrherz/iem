# Compute mixing ratio climatology

import iemdb
from pyIEM import mesonet
import math, numpy
ASOS = iemdb.connect("asos", bypass=True)
acursor = ASOS.cursor()
acursor.execute("""SELECT distinct 
extract(hour from valid + '10 minutes'::interval) as hr, tmpf, dwpf 
from alldata where station = 'AMW' and dwpf > -50 and dwpf < 90 
and tmpf > -50 and tmpf < 120 and valid > '1997-07-01'  and valid < '2011-01-01' 
and extract(month from valid) = 7 and 
extract(minute from valid + '10 minutes'::interval) between 0 and 10""")

Ttmpf = numpy.zeros( (24,), 'f')
Theat = numpy.zeros( (24,), 'f')
Tmix = numpy.zeros( (24,), 'f')
cnts = numpy.zeros( (24,), 'f')
for row in acursor:
  dwpc = mesonet.f2c( row[2] )
  e  = 6.112 * math.exp( (17.67 * dwpc) / (dwpc + 243.5));
  mixr =  0.62197 * e / (1000.0 - e)
  h = mesonet.heatidx(row[1], mesonet.relh(row[1], row[2]))

  Tmix[ row[0] -1] += mixr
  Ttmpf[ row[0] -1] += row[1]
  Theat[ row[0] -1] += h
  cnts[ row[0] - 1] += 1.0
  
import matplotlib.pyplot as plt
import matplotlib

Tmix = numpy.array(Tmix)
Ttmpf = numpy.array(Ttmpf)
Theat = numpy.array(Theat)
cnts = numpy.array(cnts)

fig = plt.figure()
ax = fig.add_subplot(211)

ax.plot(numpy.arange(0,24), Ttmpf / cnts, color='black', label='Air Temp')
ax.plot(numpy.arange(0,24), Theat / cnts, color='r', label='Heat Index')

ax2 = ax.twinx()
ax2.plot(numpy.arange(0,24), Tmix / cnts * 1000.0, color='b')

ax.set_ylim(60,120)
ax2.set_ylim(12,28)
ax.set_title("Ames [KAMW] July Hourly Climatology [1997-2010]")
ax2.set_ylabel("Mixing Ratio ($g/kg$)", color='blue')
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_xlim(0,24)
ax.grid(True)
ax.legend(loc=2)
ax.set_xticks((0,3,6,9,12,15,18,21))
ax.set_xticklabels(("Mid", '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM', '9 PM'))

#-------------------------------------------
acursor.execute("""SELECT distinct 
extract(hour from valid + '10 minutes'::interval) as hr, tmpf, dwpf 
from alldata where station = 'AMW' and dwpf > -50 and dwpf < 90 
and tmpf > -50 and tmpf < 120 and valid > '2011-07-18'  and valid < '2011-07-19' 
and extract(month from valid) = 7 and 
extract(minute from valid + '10 minutes'::interval) between 0 and 10""")

Ttmpf = numpy.zeros( (24,), 'f')
Theat = numpy.zeros( (24,), 'f')
Tmix = numpy.zeros( (24,), 'f')
cnts = numpy.zeros( (24,), 'f')
for row in acursor:
  dwpc = mesonet.f2c( row[2] )
  e  = 6.112 * math.exp( (17.67 * dwpc) / (dwpc + 243.5));
  mixr =  0.62197 * e / (1000.0 - e)
  h = mesonet.heatidx(row[1], mesonet.relh(row[1], row[2]))

  Tmix[ row[0] ] += mixr
  Ttmpf[ row[0] ] += row[1]
  Theat[ row[0] ] += h
  cnts[ row[0] ] += 1.0
  

Tmix = numpy.array(Tmix)
Ttmpf = numpy.array(Ttmpf)
Theat = numpy.array(Theat)
cnts = numpy.array(cnts)

ax = fig.add_subplot(212)
#for child in ax.get_children():
#    if isinstance(child, matplotlib.spines.Spine):
#        child.set_color('#dddddd')

ax.plot(numpy.arange(0,24), Ttmpf / cnts, color='black', label='Air Temp')
ax.plot(numpy.arange(0,24), Theat / cnts, color='r', label='Heat Index')

ax2 = ax.twinx()
ax2.plot(numpy.arange(0,24), Tmix / cnts * 1000.0, color='b')


ax.set_title("Ames [KAMW] 18 July 2011")
ax2.set_ylabel("Mixing Ratio ($g/kg$)", color='blue')
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_xlim(0,24)
ax.grid(True)
ax.legend(loc=2)
ax.set_ylim(60,120)
ax2.set_ylim(12,28)
ax.set_xticks((0,3,6,9,12,15,18,21))
ax.set_xticklabels(("Mid", '3 AM', '6 AM', '9 AM', 'Noon', '3 PM', '6 PM', '9 PM'))

for tick in ax2.yaxis.get_major_ticks():
	tick.label1.set_color('blue')

import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
