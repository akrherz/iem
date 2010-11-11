
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()
pcursor.execute("""SET TIME ZONE 'GMT'""")
def getdata(year):
    pcursor.execute("""
select s.valid, extract(doy from s.valid), ST_Area( ST_Transform( 
    ST_Intersection(s.geom, t.the_geom),26915) ) / 1000000. / 145693.8 
from spc_outlooks s, states t 
WHERE ST_Intersects(s.geom, t.the_geom) 
and t.state_name = 'Iowa' and category = 'SLGT' 
and s.valid > %s and s.valid < %s and day = 1 
and extract(hour from s.valid) = 13 
ORDER by valid ASC
    """ , ("%s-01-01" % (year,), "%s-01-01" % (year +1,) ))

    doy = []
    ratio = []

    for row in pcursor:
        doy.append( row[1] )
        ratio.append( row[2] * 100.0 )
    return doy, ratio

doy2009, ratio2009 = getdata(2009)
doy2010, ratio2010 = getdata(2010)

import matplotlib.pyplot as plt


fig = plt.figure()
ax = fig.add_subplot(211)

ax.bar( doy2009, ratio2009, edgecolor='r', facecolor='r', label='2009')
ax.set_xlim(0,366)
ax.set_ylim(0,100)
ax.set_ylabel('Iowa Areal Coverage [%]')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
ax.legend(loc=2)
ax.set_title('SPC Day 1 Convective Slight Risk\n13 UTC Morning Issuance')

ax = fig.add_subplot(212)

ax.bar( doy2010, ratio2010, edgecolor='r', facecolor='r', label='2010')
ax.set_xlim(0,366)
ax.set_ylim(0,100)
ax.set_ylabel('Iowa Areal Coverage [%]')
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlabel('*2010 Data Valid Thru 24 October')
ax.grid(True)
ax.legend(loc=2)
import iemplot
fig.savefig('test.ps')
iemplot.makefeature('test')