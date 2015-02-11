"""
 Generate analysis of precipitation
"""

import sys
from pyiem.plot import MapPlot

import datetime
now = datetime.datetime.now()

import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()


def t(value):
    """Convert into something nice"""
    if value == 0.0001:
        return 'T'
    return value

# Compute normal from the climate database
sql = """
select s.id, s.network,
  ST_x(s.geom) as lon, ST_y(s.geom) as lat,
  (case when c.pday < 0 or c.day is null then 0 else c.pday end) as rainfall
 from summary_%s c, current c2, stations s
 WHERE s.iemid = c2.iemid and c2.iemid = c.iemid and
 c2.valid > (now() - '2 hours'::interval)
 and c.day = 'TODAY'
 and s.country = 'US' and (s.network ~* 'ASOS' or s.network = 'AWOS')
 and s.state in ('IA','MN','WI','IL','MO','NE','KS','SD','ND')
""" % (now.year, )

lats = []
lons = []
vals = []
iavals = []
valmask = []
icursor.execute(sql)
for row in icursor:
    lats.append(row[3])
    lons.append(row[2])
    vals.append(t(row[4]))
    iowa = row[1] in ['AWOS', 'IA_ASOS']
    valmask.append(iowa)
    if iowa:
        iavals.append(row[4])

if len(lats) < 3:
    sys.exit(0)

m = MapPlot(title="Iowa ASOS/AWOS Rainfall Reports", axisbg='white',
            subtitle="%s" % (now.strftime("%d %b %Y"), ))
m.drawcounties()
m.plot_values(lons, lats, vals)
pqstr = "plot c 000000000000 summary/today_prec.png bogus png"
m.postprocess(view=False, pqstr=pqstr)
m.close()
