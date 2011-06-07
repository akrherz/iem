import iemdb
import numpy
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

pabr_data = {}
acursor.execute("""
    select date(valid) as d, max(tmpf), min(tmpf) from alldata 
    where station = 'PABR' and tmpf < 120 and tmpf > -90 
    and valid > '1950-01-01' GROUP by d
""")
for row in acursor:
    pabr_data[ row[0] ] = {'high': row[1], 'low': row[2]}

cnts = numpy.zeros((366,))
jdays = []
diff = []
acursor.execute("""
    select date(valid) as d, extract(doy from valid) as dy, 
    max(tmpf), min(tmpf) from alldata 
    where station = 'DSM' and tmpf < 120 and tmpf > -90 
    and valid > '1950-01-01' GROUP by d, dy
""")
for row in acursor:
    if pabr_data.has_key( row[0] ) and pabr_data[row[0]]['high'] > row[2]:
        cnts[ row[1] - 1 ] += 1.
        jdays.append( row[1] - 1 )
        diff.append(pabr_data[row[0]]['high'] - row[2] )
        if row[1] > 244 and row[1] < 274:
            print row, pabr_data[row[0]]

print numpy.sum( cnts )
import iemplot
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_xlim(0,366)
ax.bar( numpy.arange(0,366), cnts)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_ylabel('Number of Years')
ax.set_title("Barrow, Alaska warmer than Des Moines, Iowa\n1950-2010")
ax.grid(True)


ax2 = fig.add_subplot(212)
ax2.set_xlim(0,366)
ax2.set_ylim(0,50)
ax2.scatter( jdays, diff )
ax2.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax2.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax2.set_ylabel('High Temperature Difference $^{\circ}\mathrm{F}$')
ax2.grid(True)
fig.savefig('test.ps')
iemplot.makefeature('test')
