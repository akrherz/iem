import psycopg2
import numpy
from pyiem.plot import MapPlot

#bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])
#bins = numpy.array([0,1,14,31,91,135,182,227,273,365,730,1460,])
#bins = numpy.arange(0,12000.1,1000.)
bins = numpy.arange(0,101,10)

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()
pcursor.execute("""
select wfo, avg(length)  from 
(select wfo, eventid, issue, expire, array_length(regexp_split_to_array(meat, '\s+'),1) as length 
from (select wfo, eventid, issue, expire, 
split_part(split_part(report, 'PREPAREDNESS ACTIONS', 2), '&&', 1) as meat from 
warnings_2013 where phenomena in ('SV','TO') and significance = 'W' and gtype = 'P') as foo ) 
as foo2 GROUP by wfo ORDER by avg
""")

data = {}
for row in pcursor:
    if row[1] is None:
        continue
    print row
    data[ row[0] ] = row[1]
    
p = MapPlot(sector='nws',
                 title='2013 SVR+TOR Warnings Approx. Avg Word Count in Text',
                 subtitle='based on IEM archive: 1 Jan 2013 - 21 Aug 2013, preparedness actions section only')
p.fill_cwas(data, bins=bins, lblformat='%.0f', units='count')
p.postprocess(filename='test.png')
#import iemplot
#iemplot.makefeature('test')
