import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select sum(case when o.high > c.high then 1 else 0 end), 
 sum(case when o.precip >= 0.01 then 1 else 0 end), 
 count(*),
 extract(dow from day) as dow from alldata_ia o, climate51 c where 
 o.station = 'IA0200' and o.day > '2011-01-01' and 
 to_char(o.day, 'MMDD') = to_char(c.valid, 'MMDD') and c.station = 'IA0200' 
 GROUP by dow ORDER by dow
""")
freq = []
precip = []
for row in ccursor:
  freq.append( row[0] / float(row[2]) * 100. )
  precip.append( row[1] / float(row[2]) * 100. )
  
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(211)

ax.set_title("Ames Weather by Day of Week\n1 Jan 2011 - 6 Nov 2011")

bars = ax.bar(np.arange(7) -0.4, freq )
for rect, label in zip(bars, freq):
  y = rect.get_height()
  x = rect.get_x()
  ax.text(x+0.1,y-5,"%.0f %%" % (label,), weight='bold', color='white')

ax.set_xlim(-0.5, 6.5)
ax.set_xticklabels(("", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))
ax.set_ylabel("High Temp above Average")

ax2 = fig.add_subplot(212)
bars = ax2.bar(np.arange(7) -0.4, precip )
for rect, label in zip(bars, precip):
  y = rect.get_height()
  x = rect.get_x()
  ax2.text(x+0.15,y-5.,"%.0f %%" % (label,), weight='bold', color='white')
ax2.set_xticklabels(("", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))
ax2.set_xlim(-0.5, 6.5)
ax2.set_ylabel("Observed Precipitation")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
