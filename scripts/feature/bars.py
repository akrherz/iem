
from matplotlib import pyplot as plt
import numpy
import iemplot

coverage = [25.0, 34.146341463414636, 51.968503937007867, 57.964601769911503, 40.465116279069768, 18.497109826589593, 6.4864864864864868, 6.4327485380116958, 2.083333333333333, 1.680672268907563, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
avgRain = [0.75143766403198242, 0.8477320787383289, 0.98347082663708785, 1.1510259577658324, 0.86791261185047242, 0.50188304923173321, 0.2912971084182327, 0.27489973369397613, 0.2098076475991143, 0.2139480975495667, 0.20024166336978774, 0.20125648210633476, 0.12343124389648437, 0.059379973581859043, 0.11521736780802409, 0.15796695152918497, 0.0, 0.0, 0.0]
bins = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

coverage = numpy.array(coverage)
avgRain = numpy.array(avgRain)
bins = numpy.array(bins)

fig = plt.figure()
ax = fig.add_subplot(211)
bars = ax.bar(bins - 0.4, coverage, color='b', edgecolor='b')
ax.set_xlim(-7, 12)
#ax.plot((1893,2011), (numpy.average(apr1),numpy.average(apr1)), color='black') 
ax.set_ylabel("1+ inch Areal Coverage [%]")
ax.set_title("22 July 2011 Rainfall over Iowa")
ax.grid(True)

ax2 = fig.add_subplot(212)
bars = ax2.bar(bins -0.4, avgRain, color='b', edgecolor='b')
ax2.set_ylabel("Average Precipitation [inches]")
#ax2.set_xlabel("Year, 2011 thru 21 June")
ax2.set_xlabel("1 March - 21 July 2011 Deficit [inches]")
ax2.set_xlim(-7,12)
ax2.grid(True)



plt.savefig('test.ps')
iemplot.makefeature("test")
