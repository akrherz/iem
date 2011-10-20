import iemdb 
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import numpy
cnts = numpy.zeros( (7,51), 'f') # 50 to 100

sz = 0
for yr in range(1893,2011):
  ccursor.execute("""
   SELECT high from alldata_ia WHERE station = 'IA0200' and
   sday > '1019' and year = %s ORDER by high DESC LIMIT 7
  """ % (yr,))
  i = 0
  sz += 1
  for row in ccursor:
    pos = row[0] - 50 + 1
    cnts[i,:pos] += 1.0
    i += 1

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Ames High Temperature Frequencies per Number of Days\nfor dates after 19 Oct till 31 Dec [1893-2010]")
ax.set_xlabel("High Temperature $^{\circ}\mathrm{F}$")
ax.set_ylabel("Observed Frequency [%]")
ax.grid(True)
colors = ['blue','green','red','teal','purple','gold','black']

for i in range(7):
  data = cnts[i,:] / float(sz) * 100.0
  ax.plot(numpy.arange(50,101), data, color=colors[i])
  for j in range(len(data)):
    if data[j] < 50:
      ax.text(j+50, data[j], "%s" % (i+1,), color=colors[i])
      break

ax.text(80,80, "Example: We have ~80% chance\nof one day over 70, but ~20%\n chance of 7 days over 70", bbox=dict(color='#EEEEEE',boxstyle='round'))

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
