"""
 Generate a plot of GDD 
"""

from pyiem.plot import MapPlot
import datetime
import numpy as np
import psycopg2
COOP = psycopg2.connect("dbname=coop host=iemdb user=nobody")
ccursor = COOP.cursor()

import network
nt = network.Table("IACLIMATE")

def run(base, ceil, now, fn):
    """ Generate the plot """
    # Compute normal from the climate database
    ccursor.execute("""
    SELECT station, sum(gdd50) from climate51 WHERE 
    station != 'IA0000' and substr(station,2,1) != 'C' and
    valid >= '2000-05-01' and valid < '2000-09-25' GROUP by station
    """)
    normal = {}
    for row in ccursor:
        normal[ row[0] ] = row[1]
    
    sql = """SELECT station,
       sum(gddxx(%s, %s, high, low)) as gdd
       from alldata_ia WHERE year = %s and month in (5,6,7,8,9,10)
       and station != 'IA0000' and substr(station,2,1) != 'C'
       GROUP by station""" % (base, ceil, now.year)

    lats = []
    lons = []
    gdd50 = []
    ccursor.execute( sql )
    for row in ccursor:
        if not nt.sts.has_key(row[0]):
            continue
        lats.append( nt.sts[row[0]]['lat'] )
        lons.append( nt.sts[row[0]]['lon'] )
        gdd50.append( float(row[1]) - normal[row[0]] )
    print gdd50, max(gdd50), min(gdd50)
    m = MapPlot(sector='iowa', title='1 May - 24 Sep 2013 Growing Degree Day Departure')
    m.contourf(lons, lats, gdd50, np.arange(-300,301,50))
    m.postprocess(filename='test.ps')
    import iemplot
    iemplot.makefeature('test')
if __name__ == '__main__':
    today = datetime.datetime.now()
    if today.month < 5:
        today = today.replace(year=(today.year-1), month=11, day=1)
    run(50,86, today, 'gdd_may1')
