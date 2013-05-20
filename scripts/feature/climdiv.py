from pyiem.plot import MapPlot
import numpy
import psycopg2

dbconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = dbconn.cursor()
clim = {}
cursor.execute("""SELECT station, avg(sum) from 
  (SELECT station, year, sum(precip) from alldata where
  year < 2013 and year > 1950 and substr(station,3,1) = 'C' and month in (4,5) 
  and sday < '0520' GROUP by station, year) as foo
  GROUP by station""")
for row in cursor:
  clim[ row[0] ] = row[1]

data = {}
cursor.execute("""SELECT station, sum(precip) from alldata where
  year = 2013 and substr(station,3,1) = 'C' and month in (4,5) GROUP by station""")
for row in cursor:
  data[ row[0] ] = row[1] - clim[ row[0] ]

m = MapPlot(sector='midwest', title='IEM Estimated Climate Division Precipitation Departure [inch]', subtitle='1 April thru 19 May 2013 vs 1950-2012 Climate')
m.fill_climdiv(data, bins=numpy.arange(5,-5.1,-0.25), lblformat='%.1f')
m.postprocess(filename='test.svg')
import iemplot
iemplot.makefeature('test')
