import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

# July
ccursor.execute("""
 SELECT avg((high+low)/2.) from alldata where stationid = 'ia2203' and month = 7 
 and year > 1892
""")
row = ccursor.fetchone()
july = row[0]
print july
# August
ccursor.execute("""
 SELECT avg((high+low)/2.) from alldata where stationid = 'ia2203' and month = 8 
 and year > 1892
""")
row = ccursor.fetchone()
august = row[0]

yearly_july = []
ccursor.execute("""
 SELECT year, avg((high+low)/2.) from alldata where stationid = 'ia2203' and month = 7 and year < 2011 and year > 1892
 GROUP by year ORDER by year ASC
""")
for row in ccursor:
    yearly_july.append( float(row[1] - july) )

yearly_aug = []
ccursor.execute("""
 SELECT year, avg((high+low)/2.0) from alldata where stationid = 'ia2203' and month = 8 and year < 2011 and year > 1892
 GROUP by year ORDER by year ASC
""")
for row in ccursor:
    yearly_aug.append( float(row[1] - august) )

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Des Moines July then August Average Temp")

ax.scatter( yearly_july, yearly_aug )
ax.plot([-10,10],[-10,10])
ax.plot([5.5,5.5],[-10,10], color='r')
ax.plot([5.2,5.8],[3.,3.], color='r')
ax.text(5.8,3.1,'1-10 Aug 2011', color='r')
ax.set_xlim(-10,10)
ax.set_ylim(-10,10)
ax.set_ylabel("August Temperature Departure $^{\circ}\mathrm{F}$")
ax.set_xlabel("July Temperature Departure $^{\circ}\mathrm{F}$")
ax.text( 7,-8, "$R^{2}$ = %.1f" % ((numpy.corrcoef(yearly_july, yearly_aug)[0,1]) ** 2,))
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
