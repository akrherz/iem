"""
Compute the amount of precipitation that falls during a SVR,TOR warning
"""
import iemdb
import numpy
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()


total_in = numpy.zeros((2013-2002), 'f')
total_out = numpy.zeros((2013-2002), 'f')
total_arr = numpy.zeros((2013-2002), 'f')

for year in range(2002,2013):
    warntimes = []
    around = []
    pcursor.execute("""
     select generate_series(issue, expire, '1 minute'::interval) from warnings_%s 
     where wfo = 'DMX' and phenomena in ('SV','TO') and significance = 'W' 
     and gtype = 'P' 
     and ST_Contains(geom, GeomFromEWKT('SRID=4326;POINT(-93.66308 41.53397)'))
    """ % (year,))
    for row in pcursor:
        if row[0] not in warntimes:
            warntimes.append( row[0] )
    
    pcursor.execute("""
     select generate_series(issue - '1 hour'::interval, 
         expire + '1 hour'::interval, '1 minute'::interval) from warnings_%s 
     where wfo = 'DMX' and phenomena in ('SV','TO') and significance = 'W' 
     and gtype = 'P' 
     and ST_Contains(geom, GeomFromEWKT('SRID=4326;POINT(-93.66308 41.53397)'))
    """ % (year,))
    for row in pcursor:
        if row[0] not in around:
            around.append( row[0] )
        
    # Get rainfall
    acursor.execute("""
        SELECT valid, precip from t%s_1minute where station = 'DSM' and precip > 0
        
    """ % (year,))

    print year, acursor.rowcount, len(warntimes), len(around)
    for row in acursor:
        if row[0] in warntimes:
            total_in[row[0].year-2002] += row[1]
            warntimes.remove(row[0])
        elif row[0] in around:
            total_arr[row[0].year-2002] += row[1] 
            around.remove(row[0])
        else:
            total_out[row[0].year-2002] += row[1]
            
print total_in
print total_arr
print total_out

import matplotlib.pyplot as plt

fig, ax = plt.subplots(2,1, sharex=True)

ax[0].set_xlim(2001.5,2012.5)
ax[1].set_xlabel("*2012 thru 5 June")
ax[0].set_ylabel("Yearly Precip [inch]")
ax[1].set_ylabel("Percentage [%]")
ax[1].set_ylim(0,100)
ax[0].set_title("Des Moines Yearly Airport Precipitation [2002-2012]\nContribution during, around, and outside of TOR,SVR warning")
ax[0].bar(numpy.arange(2002,2013)-0.4, total_in, fc='r')
ax[0].bar(numpy.arange(2002,2013)-0.4, total_arr, bottom=total_in, fc='b')
ax[0].bar(numpy.arange(2002,2013)-0.4, total_out, bottom=(total_in+total_arr), fc='g')

p = total_in / (total_in + total_out + total_arr) * 100.0
ax[1].bar(numpy.arange(2002,2013)-0.4, p, fc='r', label='During')

p2 = total_arr / (total_in + total_out + total_arr) * 100.0
ax[1].bar(numpy.arange(2002,2013)-0.4, p2, bottom=p, fc='b', label='+/- 1 hour')

p3 = total_out / (total_in + total_out + total_arr) * 100.0
ax[1].bar(numpy.arange(2002,2013)-0.4, p3, bottom=(p+p2), fc='g', label='Outside')

ax[1].legend(ncol=3, loc=(0.13,1.01))
ax[1].grid(True)
ax[0].grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')