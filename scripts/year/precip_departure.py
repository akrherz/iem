from pyiem.plot import MapPlot
import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()
from pyiem.network import Table as NetworkTable
import numpy as np
import sys
import matplotlib.cm as cm
nt = NetworkTable("IACLIMATE")

rejs = ['IA5493', 'IA0000','IA1954', 'IA1394']

def run(year):
    cursor.execute("""
    WITH obs as (
    SELECT station, sum(precip) from alldata_ia where year = %s GROUP by station
    ), climate as (
    SELECT station, sum(precip) from climate51 GROUP by station
    )
    SELECT o.station, o.sum - c.sum as diff from obs o JOIN climate c 
    on (c.station = o.station) ORDER by diff ASC
    """, (year,))
    lats = []
    lons = []
    vals = []
    for row in cursor:
        if not nt.sts.has_key(row[0]) or row[0] in rejs or row[0][2] == 'C':
            continue
        print row
        lats.append( nt.sts[row[0]]['lat'])
        lons.append( nt.sts[row[0]]['lon'])
        vals.append( row[1] )
    
    m = MapPlot(title='%s Precipitation Departure' % (year,))
    cmap = cm.get_cmap('BrBG')
    #cmap.set_over('blue')
    #cmap.set_under('red')
    m.contourf(lons, lats, vals, np.arange(-24,24.1,2), cmap=cmap, units='inch')
    #m.plot_values(lons, lats, vals, '%.02f')
    m.drawcounties()
    m.postprocess(filename='%s.png' % (year,))
    
run(sys.argv[1])