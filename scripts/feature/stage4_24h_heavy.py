"""
Create a plot of today's total precipitation from the Stage4 estimates
"""
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()
import pygrib
import mx.DateTime
import iemplot
import numpy
import os, sys
from pyiem.plot import MapPlot

dlats = []
dlons = []
dvals = []
cursor.execute("""
  SELECT id, x(geom) as lon, y(geom) as lat, sum(pday) from summary_2013 s
  JOIN stations t on (t.iemid = s.iemid) WHERE t.network = 'IA_ASOS' and
  day >= '2013-05-25' and pday > 0 GROUP by id, lon, lat
""")
for row in cursor:
    dlats.append( row[2] )
    dlons.append( row[1] )
    dvals.append( row[3] )

def doday():
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    sts = mx.DateTime.DateTime(2013,5,25,12)
    ets = mx.DateTime.DateTime(2013,5,31,12)
    interval = mx.DateTime.RelativeDateTime(days=1)
    now = sts
    total = None
    while now < ets:
        fp = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.24h.grib" % (
            now.strftime("%Y/%m/%d"), 
            now.strftime("%Y%m%d%H") )
        if os.path.isfile(fp):
            lts = now
            grbs = pygrib.open(fp)

            if total is None:
                g = grbs[1]
                total = g["values"]
                lats, lons = g.latlons()
            else:
                total += grbs[1]["values"]
            grbs.close()
        now += interval
        
    m = MapPlot(sector='iowa', title='NOAA Stage IV & Iowa ASOS Precipitation',
                subtitle='25-30 May 2013')
    m.pcolormesh(lons, lats, total / 25.4, numpy.arange(0,14.1,1), latlon=True,
                 units='inch')
    m.drawcounties()
    m.plot_values(dlons, dlats, dvals, '%.02f')
    m.postprocess(filename='test.svg')
    import iemplot
    iemplot.makefeature('test')

if __name__ == "__main__":
    doday()
