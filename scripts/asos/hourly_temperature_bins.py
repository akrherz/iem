"""
Compute hourly bins of temperature
"""
import mx.DateTime
import iemdb
import numpy
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

# -50 to 120, 85
counts = numpy.zeros( (85,12), 'f')

acursor.execute("""
 SELECT to_char(valid, 'YYYYmmddHH24') as h, avg(tmpf) from t2008
 WHERE station = 'DEH' and tmpf is not null GROUP by h
""")

for row in acursor:
    ts = mx.DateTime.strptime(row[0], '%Y%m%d%H')
    bin = (row[1] + 50 ) / 2.0
    counts[int(bin), ts.month -1 ] += 1

print 'AvgT,BinRange,Total,J,F,M,A,M,J,J,A,S,O,N,D,%TOT,CUM%'    

total = acursor.rowcount
running = 0

for bin in range(84,-1,-1):
    bottom = (bin * 2) + -50
    running += numpy.sum(counts[bin,:])
    print '%s,%s to %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%.2f,%.2f' % (bottom+1, bottom, bottom+2, numpy.sum(counts[bin,:]),
            counts[bin,0], counts[bin,1], counts[bin,2], counts[bin,3],
            counts[bin,4], counts[bin,5], counts[bin,6], counts[bin,7],
            counts[bin,8], counts[bin,9], counts[bin,10], counts[bin,11],
            numpy.sum(counts[bin,:]) / float(total) * 100.0,
            100 - running / float(total) * 100.0)