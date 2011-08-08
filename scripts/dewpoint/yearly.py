import iemdb
import math
import numpy
from pyIEM import mesonet
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()

climate = numpy.zeros( (24,2012-1951), 'f')

# Find list of stations
stations = []
mcursor.execute("""
    SELECT id from stations WHERE network in ('IA_ASOS', 'MO_ASOS','KS_ASOS','NE_ASOS','SD_ASOS','ND_ASOS',
    'MN_ASOS','WI_ASOS','IL_ASOS','IN_ASOS','MI_ASOS') and archive_begin < '1960-01-01'
    """)
for row in mcursor:
    stations.append( row[0] )
stations = ['CID','XXXXX']
for yr in range(1951,2012):
    acursor.execute("""
    SELECT valid + '10 minutes'::interval, tmpf, dwpf from t%s WHERE station in %s
    and extract(month from valid) = 7 and dwpf > -30 and tmpf > -30
    """ % (yr, str(tuple(stations))))
    hourly = numpy.zeros( (24,), 'f')
    counts = numpy.zeros( (24,), 'f')
    for row in acursor:
        dwpc = mesonet.f2c( row[2] )
        e  = 6.112 * math.exp( (17.67 * dwpc) / (dwpc + 243.5))
        mixr =  0.62197 * e / (1000.0 - e)
        if mixr > 0:
            hourly[ row[0].hour - 1] += mixr
            counts[ row[0].hour - 1] += 1
        
    climate[:,yr-1951] = hourly / counts * 1000.
    avgV = numpy.sum(hourly) / numpy.sum(counts) * 1000.
    print yr, avgV 
    
    

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

res = ax.imshow( climate, aspect='auto', interpolation='nearest' )
clr = fig.colorbar(res)
clr.ax.set_ylabel("g/kg")

ax.set_ylim(-0.5,23.5)
ax.set_yticks( numpy.arange(0,24,4))
ax.set_yticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xticks( numpy.arange(0,61,10) )
ax.set_xticklabels( numpy.arange(1951,2012,10) )
ax.set_title("Mid-West July Average Hourly Mixing Ratio (1951-2011)")

fig.savefig('test.png')
