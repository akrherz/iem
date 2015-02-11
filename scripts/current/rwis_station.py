"""Iowa RWIS station plot!
"""
import datetime
now = datetime.datetime.now()
from pyiem.plot import MapPlot
import psycopg2.extras
from pyiem.datatypes import direction, speed
import pyiem.meteorology as meteorology
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Compute normal from the climate database
sql = """
SELECT 
  s.id, tmpf, dwpf, sknt, drct,  ST_x(s.geom) as lon, ST_y(s.geom) as lat
FROM 
  current c, stations s 
WHERE
  s.network IN ('IA_RWIS') and c.iemid = s.iemid and 
  valid + '20 minutes'::interval > now() and
  tmpf > -50 and dwpf > -50
"""

data = []
icursor.execute(sql)
for row in icursor:
    data.append(row)

m = MapPlot(axisbg='white',
            title='Iowa DOT RWIS Mesoplot',
            subtitle='plot valid %s' % (now.strftime("%-d %b %Y %H:%M %P"), ))
m.plot_station(data)
m.drawcounties(color='#EEEEEE')
pqstr = "plot c 000000000000 iowa_rwis.png bogus png"
m.postprocess(pqstr=pqstr)
m.close()
