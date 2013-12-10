import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

data = numpy.zeros( (2010-1893, 2), 'f')

ccursor.execute("""
    SELECT year, min(extract(doy from day)), 
    max(extract(doy from day)) from alldata where 
    stationid = 'ia2203' and high > 69 and year > 1892 GROUP by year
""")
for row in ccursor:
    year = row[0]
    mn = row[1]
    mx = row[2]
    if year > 1893:
        data[ year-1893 -1, 1] = mn + 365.
    if year < 2010:
        data[ year-1893, 0] = mx
        
n = numpy.min(data[:,1] - data[:,0])
x = numpy.max(data[:,1] - data[:,0])
nx = numpy.where((data[:,1] - data[:,0]) == n)
xx = numpy.where((data[:,1] - data[:,0]) == x)


import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

def modrects(rects, a):
	for rect in rects:
		if rect.get_width() > a:
			rect.set_facecolor('b')
			rect.set_edgecolor('b')
		else:
			rect.set_facecolor('r')
			rect.set_edgecolor('r')

print numpy.shape( data[:,1])
rects = ax.barh( numpy.arange(1893,2010) - 0.3, data[:,1] - data[:,0], left=data[:,0], edgecolor='b')
modrects( rects, numpy.average(data[:,1] - data[:,0])  )
ax.set_ylim(1892.5, 2009.5)
ax.grid(True)
ax.set_xticks( (274,305,335,365,365+32,365+60,365+91,365+121) )
ax.set_xticklabels( ('Oct 1','Nov 1', 'Dec 1', 'Jan 1', 'Feb 1', 'Mar 1', 'Apr 1','May 1'))
ax.set_xlim(270, 365+121)
ax.set_title("Des Moines Winter Period Sub 70$^{\circ}\mathrm{F}$\nMin: %.0f days (%.0f) Max: %.0f days (%.0f) Avg: %.0f days" % (
                                                                                                 
                                                        n, nx[0]+1893, x, xx[0]+1893,numpy.average(data[:,1] - data[:,0]) ))
ax.set_ylabel('Year')
ax.set_xlabel('Period of last 70$^{\circ}\mathrm{F}$ to first 70$^{\circ}\mathrm{F}$')
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')
