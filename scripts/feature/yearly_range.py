import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
    SELECT year, high, low from alldata_ia where station = 'IA0200'
    and sday = '1225' and year > 1892 ORDER by year ASC
""")

bottom = []
height = []

for row in ccursor:
    bottom.append( row[2] )
    height.append( row[1] - row[2] )

#bottom.append(31)
#height.append(15)

bottom = numpy.array( bottom )
height = numpy.array( height )
import matplotlib.pyplot as plt
import iemplot

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( numpy.arange(1893, 2012) - 0.4, height, bottom=bottom,
        facecolor='#00FF00', edgecolor='#00FF00', zorder=1)
red = 0
blue = 0
for bar in bars:
    if (bar.get_height() + bar.get_y()) >= 45:
        bar.set_facecolor('#ff0000')
        bar.set_edgecolor("#ff0000")
        red += 1
    if (bar.get_height() + bar.get_y()) < 32:
        bar.set_facecolor('#0000ff')
        bar.set_edgecolor("#0000ff")
        blue += 1
ax.set_xlim(1892.5, 2011.5)
ax.set_title("Ames Christmas Day High + Low Temperature [1893-2011]")
ax.grid(True)
ax.text(1910, -16, 'Low Temp above 30$^{\circ}\mathrm{F}$ (%s/%s years)' % (
                                    blue, len(height)), color='b')
ax.text(1910, -19, 'High Temp above 45$^{\circ}\mathrm{F}$ (%s/%s years)' % (
                                    red, len(height)), color='r')
ax.legend(loc=2)
ax.set_ylabel('Temperature $^{\circ}\mathrm{F}$')
fig.savefig('test.ps')
iemplot.makefeature('test')