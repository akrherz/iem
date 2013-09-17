import psycopg2
from pyiem.plot import MapPlot

MESOSITE = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
mcursor = MESOSITE.cursor()

lats = []
lons = []
vals = []
for line in open('UTC_OFFSET.txt'):
    tokens = line.split(",")
    sid = tokens[0]
    state = tokens[3]
    offset = tokens[4].strip()
    mcursor.execute("""SELECT x(geom), y(geom) from stations where id = %s
    and network ~* 'ASOS' """ , (sid,))
    if mcursor.rowcount == 1:
        row = mcursor.fetchone()
        if offset[0] != '-':
            print tokens
        vals.append( offset )
        lats.append( row[1] )
        lons.append( row[0] )

m = MapPlot('conus', figsize=(12,9))
m.plot_values(lons, lats, vals, '%s')
m.postprocess(filename='offset.png')