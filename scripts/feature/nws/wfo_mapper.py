import psycopg2
import numpy
from pyiem.plot import MapPlot

#bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])
#bins = numpy.array([0,1,14,31,91,135,182,227,273,365,730,1460,])
#bins = numpy.arange(0,12000.1,1000.)
#bins = numpy.arange(0,201,20)
bins = [0,20,40,60,80,100,150,200,250,300,500,700,1000]

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()
pcursor.execute("""

select wfo, max(case when year = 2013 then count else 0 end) /
    (sum(case when year < 2013 then count else 0 end)/10.0) * 100.0 as d,
     max(case when year = 2013 then count else 0 end),
    sum(case when year < 2013 then count else 0 end)/10.0
     from 
    (select wfo, year, count(*) from 
        (select distinct extract(year from issue) as year, wfo, phenomena, eventid from 
        warnings WHERE extract(doy from issue) < 270 and issue > '2003-01-01' 
        and phenomena in ('FF') and significance = 'W') as foo 
        GROUP by wfo, year) as foo2 
GROUP by wfo ORDER by d DESC

""")

data = {}
for row in pcursor:
    if row[1] is None:
        continue
    print row
    data[ row[0] ] = row[1] 
    
p = MapPlot(sector='nws',
                 title='1 Jan - 26 Sep 2013 FFW Warning Count Percent of Average',
                 subtitle='Departure from 10 year average 2003-2012, year to date')
p.fill_cwas(data, bins=bins, lblformat='%.0f', units='%')
p.postprocess(filename='test.png')
#import iemplot
#iemplot.makefeature('test')
