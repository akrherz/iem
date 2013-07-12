import iemdb
import numpy
from pyiem import plot

#bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])
bins = numpy.array([0,1,14,31,91,135,182,227,273,365,730,1460,])
#bins = numpy.arange(0,12000.1,1000.)

POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()
pcursor.execute("""
 select wfo, max(d) from (select wfo, 
 issue - lag(issue) over (partition by wfo order by issue ASC) as d 
 from warnings where significance = 'W' and phenomena = 'TO' and 
 gtype = 'P') as foo GROUP by wfo ORDER by max ASC
""")

data = {}
for row in pcursor:
    if row[1] is None:
        continue
    print row
    data[ row[0] ] = row[1].days

p = plot.MapPlot(sector='nws',
                 title='Maximum Number of Days in-between issuing Tornado Warning',
                 subtitle='based on IEM archive: 1 Jan 2002 - 12 Jul 2013')
p.fill_cwas(data, bins=bins, lblformat='%.0f', units='days')
p.postprocess(filename='test.png')
#import iemplot
#iemplot.makefeature('test')
