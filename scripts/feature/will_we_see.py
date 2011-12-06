import iemdb 
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

import numpy
cnts = numpy.zeros( (7,71), 'f') # -40 to 30

sz = 0
for yr in range(1893,2011):
  ccursor.execute("""
   SELECT low from alldata_ia WHERE station = 'IA0200' and
   sday > '1019' and year = %s ORDER by low ASC LIMIT 7
  """ % (yr,))
  i = 0
  sz += 1
  for row in ccursor:
    if row[0] > 29:
        sys.exit()
    pos = row[0] + 40
    cnts[i,pos:] += 1.0
    i += 1

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Ames Low Temperature Frequencies per Number of Days\nfor dates after 19 Oct till 31 Dec [1893-2010]")
ax.set_xlabel("Low Temperature $^{\circ}\mathrm{F}$")
ax.set_ylabel("Observed Frequency [%]")
ax.grid(True)
colors = ['blue','green','red','teal','purple','gold','black']

for i in range(7):
  data = cnts[i,:] / float(sz) * 100.0
  ax.plot(numpy.arange(-40,31), data, color=colors[i])
  for j in range(len(data)):
    if data[j] > 50:
      ax.text(-40 + j - 0.3, data[j], "%s" % (i+1,), color=colors[i], ha="right")
      break

ax.text(1,10, "Example: We have ~80% chance\nof one day with a low of 0 or less,\nbut ~30% chance of 7 days below 0", bbox=dict(color='#EEEEEE',boxstyle='round'))
ax.set_xlim(-30,30)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
