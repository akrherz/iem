# Plot the High + Low Temperatures

import sys
from pyiem.plot import MapPlot

import datetime
now = datetime.datetime.now() - datetime.timedelta(days=int(sys.argv[1]))

import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
SELECT
  s.id as station, max_tmpf, min_tmpf, ST_x(s.geom) as lon, ST_y(s.geom) as lat
FROM
  summary_%s c, stations s
WHERE
  c.iemid = s.iemid and
  s.network IN ('AWOS', 'IA_ASOS') and
  day = '%s'
  and max_tmpf > -50
""" % (now.year, now.strftime("%Y-%m-%d"))

data = []
icursor.execute(sql)
for row in icursor:
    data.append(dict(lat=row[4], lon=row[3], tmpf=row[1], dwpf=row[2],
                id=row[0]))

m = MapPlot(title="Iowa High & Low Air Temperature", axisbg='white',
            subtitle=now.strftime("%d %b %Y"))
m.plot_station(data)
m.drawcounties()
if sys.argv[1] == "0":
    pqstr = "plot c 000000000000 summary/asos_hilo.png bogus png"
else:
    pqstr = "plot a %s0000 bogus hilow.gif png" % (now.strftime("%Y%m%d"), )
m.postprocess(view=False, pqstr=pqstr)
m.close()
