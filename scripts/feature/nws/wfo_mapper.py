import psycopg2
import datetime
#import numpy as np
from pyiem.plot import MapPlot

#bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])
#bins = numpy.array([0,1,14,31,91,135,182,227,273,365,730,1460,])
#bins = numpy.arange(0,12000.1,1000.)
#bins = numpy.arange(0,201,20)
#bins = [0,50,100,150,200,250,300,500,750,1000,1500,2000,2500,3000,3500]
#bins = [0,25,50,75,100,150,200,250,300,400,500,750,1000,1250]
#bins = [0,0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,2,2.5,3,4,6,]
bins = [1,32,60,91,121,152,182,213,244,274,305,335,365]
clabels =['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

POSTGIS = psycopg2.connect(database='postgis', host='mesonet.agron.iastate.edu', user='nobody')
pcursor = POSTGIS.cursor()
pcursor.execute("""
   SELECT wfo, avg(min) from 
   (SELECT wfo, extract(year from issue) as yr, min(extract(doy from issue))
   from warnings where phenomena = 'SV' and significance = 'W' 
   and issue < '2014-01-01' GROUP 
   by wfo, yr) as foo
   GROUP by wfo
""")

data = {}
labels = {}
for row in pcursor:
    if row[1] is None:
        continue
    ts = datetime.datetime(2000,1,1) + datetime.timedelta(days=(row[1]-1))
    labels[ row[0] ] = "%s %s%s" % (ts.strftime("%-d"), ts.strftime("%b")[0],
                           ts.strftime("%b")[2])
    data[ row[0] ] = row[1] 
    
p = MapPlot(sector='nws',
                 title="Average Date of First Sever T'Storm Warning by NWS Forecast Office",
                 subtitle='based on data from 1986-2013')
p.fill_cwas(data, bins=bins, labels=labels, lblformat='%s', clevlabels=clabels)
p.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')
