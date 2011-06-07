import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
import numpy.ma

# 1964 - 2009, 1 Nov - 1 Apr 
obs = numpy.ma.zeros( (2009-1964+1, 152), 'f')


ccursor.execute("""
 SELECT year, extract(doy from day), snowd from alldata
 WHERE day >= '1964-11-01' and stationid = 'ia0200' and
 month in (11,12,1,2,3) and snowd > 0
""")
for row in ccursor:
	year = row[0]
	doy = row[1]
	val = row[2]
	if doy > 180:
		doy = doy - 365
	else:
		year -= 1
	obs[ year - 1964, doy + 61 ] = val

obs.mask = numpy.where( obs == 0, True, False)

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111)
ax.set_xticks( (0,29,60,91,120,151) )
ax.set_xticklabels( ('Nov 1', 'Dec 1','Jan 1', 'Feb 1',
	'Mar 1', 'Apr 1') )
ax.set_yticklabels( numpy.arange(1965,2010,5) )
ax.set_yticks( numpy.arange(1,49,5) )
ax.set_ylabel('Year')
ax.set_xlabel('Date of Winter Season')
ax.set_title('Ames Daily Snow Depth (1964-2009) [inches]')

res = ax.imshow( obs, aspect='auto', rasterized=True, 
	interpolation='nearest', vmin=0, vmax=27)
fig.colorbar( res )
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test') 