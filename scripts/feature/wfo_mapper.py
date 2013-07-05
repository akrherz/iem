import iemdb
import numpy
from pyiem import plot

#bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])
bins = numpy.arange(0,12000.1,1000.)

POSTGIS = iemdb.connect('afos', bypass=True)
pcursor = POSTGIS.cursor()
pcursor.execute("""
select wfo, avg(length) from (SELECT substr(source,2,3) as wfo, length(data)from products
  WHERE substr(pil,1,3) = 'AFD' and entered > '2009-01-01' 
  and source is not null ) as foo GROUP by wfo
""")

data = {}
for row in pcursor:
    
    print row
    data[ row[0] ] = row[1] 

p = plot.MapPlot(sector='nws',
                 title='Average Character Count of Area Forecast Discussions per Day',
                 subtitle='based on IEM archive: 1 Jan 2009 - 3 Jul 2013')
p.fill_cwas(data, bins=bins, lblformat='%.0f', units='characters')
p.postprocess(filename='test.png')
#import iemplot
#iemplot.makefeature('test')
