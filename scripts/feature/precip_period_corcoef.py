import numpy
import mx.DateTime
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

precip = numpy.zeros( (2012-1894,365), 'f')

ccursor.execute("""
 SELECT extract(doy from day + '3 months'::interval) as doy, 
 extract(year from day + '3 months'::interval) as yr, precip from 
 alldata_ia where station = 'IA0200' and sday != '0229' and precip > 0
 and day > '1893-10-01' and day < '2011-10-01'
""")
for row in ccursor:
    precip[ row[1]-1894, row[0]-1] = row[2]
    
yearlyprecip = numpy.sum(precip,1)
for window in [1,7,14,21,28,30,45,60,90,365]:
    maxcoef = 0
    maxx = 0
    for x in range(0, 366-window):
        period = numpy.sum(precip[:,x:x+window], 1)
        coef = numpy.corrcoef(period, yearlyprecip)[0,1]
        if coef > maxcoef:
            maxx = x
            maxcoef = coef
    sts = mx.DateTime.DateTime(2000,10,1) + mx.DateTime.RelativeDateTime(days=maxx)
    ets = mx.DateTime.DateTime(2000,10,1) + mx.DateTime.RelativeDateTime(days=maxx+window)
    print 'Window: %s days cor-coef: %.3f Period: %s %s' % (window, maxcoef,
                                            sts.strftime("%d %b"),
                                            ets.strftime("%d %b"))