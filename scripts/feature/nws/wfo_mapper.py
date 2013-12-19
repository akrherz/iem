import psycopg2
#import numpy as np
from pyiem.plot import MapPlot

#bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])
#bins = numpy.array([0,1,14,31,91,135,182,227,273,365,730,1460,])
#bins = numpy.arange(0,12000.1,1000.)
#bins = numpy.arange(0,201,20)
#bins = [0,50,100,150,200,250,300,500,750,1000,1500,2000,2500,3000,3500]
#bins = [0,25,50,75,100,150,200,250,300,400,500,750,1000,1250]
bins = [0,0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,2,2.5,3,4,6,]

POSTGIS = psycopg2.connect(database='postgis', host='mesonet.agron.iastate.edu', user='nobody')
pcursor = POSTGIS.cursor()
pcursor.execute("""
WITH lsrcount as (
SELECT wfo, count(*) / 6.0 as a from 

(select distinct wfo, geom, typetext, magnitude, valid from lsrs WHERE
 valid > '2008-01-01' and type in ('T','H','G','D','M','W','F','x')) as foo

GROUP by wfo),
    vteccount as (
    SELECT wfo, count(*) / 6.0 as a from 

(select distinct wfo, phenomena, extract(year from issue), eventid from sbw WHERE
 issue > '2008-01-01' and significance = 'W' and 
 phenomena in ('SV','TO','FF','MA')) as foo2

GROUP by wfo
    
    )

SELECT lsrcount.wfo, lsrcount.a / vteccount.a as ratio from vteccount JOIN lsrcount on (lsrcount.wfo = vteccount.wfo)
ORDER by ratio DESC
    
""")

data = {}
for row in pcursor:
    if row[1] is None:
        continue
    print row
    data[ row[0] ] = row[1] 
    
p = MapPlot(sector='nws',
                 title='1 Jan 2008 - 18 Dec 2013 Ratio of Unique LSRs to Warnings',
                 subtitle='ratio of severe/flash flood LSRs to warnings issued')
p.fill_cwas(data, bins=bins, lblformat='%.1f', units='1')
p.postprocess(filename='test.png')
#import iemplot
#iemplot.makefeature('test')
