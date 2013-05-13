import iemdb
import numpy
from pyiem import plot
import network
nt = network.Table("IACLIMATE")

bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])

POSTGIS = iemdb.connect('coop', bypass=True)
pcursor = POSTGIS.cursor()

pcursor.execute("""
WITH data as (
select station, count(*) from (select one.station, one.day, two.day, low, high from (select station, day, low from alldata_ia where low < 40 and day >= '1951-01-01') as one, (select station, day, high from alldata_ia where high >= 90) as two where one.day = (two.day - '2 day'::interval) and one.station = two.station) as foo GROUP by station) 

SELECT station, ST_X(geom), ST_Y(geom), count from data d JOIN stations t on (d.station = t.id)
""")
lons = []
lats = []
vals = []
for row in pcursor:
    if row[0][2] == 'C' or row[0] == 'IA0000':
        continue
    if not nt.sts.has_key(row[0]):
        continue
    lons.append( row[1] )
    lats.append( row[2] )
    vals.append( row[3] )

p = plot.MapPlot(sector='iowa',
                 title='Events of Sub 40 Degrees to 90+ in Two Days',
                 subtitle='Based on Iowa Climate sites 1951-2012')
p.plot_values(lons, lats, vals, textsize=20)
p.postprocess(filename='test.svg')
import iemplot
iemplot.makefeature('test')
