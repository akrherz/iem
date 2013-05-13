import iemdb
import numpy
from pyiem import plot

#bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])
bins = numpy.arange(0,110,5)

POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

pcursor.execute("""
with total as (
select distinct wfo, 
 date(generate_series(issue, expire, '1 minute'::interval)) from warnings 
 where phenomena = 'FW' and significance = 'W' and issue > '2007-01-01'
)
SELECT wfo, count(*) from total GROUP by wfo
""")

#pcursor.execute("""
# select (case when source = 'TJSJ' then 'TSJU' else source end) as src, 
# count(*) from products where 
# substr(pil,1,3) = 'FWS' and entered > '2009-01-01' 
# and source is not null group by src order by count
#""")
data = {}
for row in pcursor:
    data[ row[0] ] = row[1] / (6.36)

p = plot.MapPlot(sector='nws',
                 title='Average # Days with a Red Flag Warning per Year',
                 subtitle='based on VTEC product counts for period: 1 Jan 2007 - 12 May 2013')
p.fill_cwas(data, bins=bins, lblformat='%.1f')
p.postprocess(filename='test.png')
import iemplot
iemplot.makefeature('test')
