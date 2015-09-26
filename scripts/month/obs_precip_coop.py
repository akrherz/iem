# Generate a map of this month's observed precip

from pyiem.plot import MapPlot
import psycopg2

import datetime
now = datetime.datetime.now()

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """SELECT id,
    sum(pday) as precip,
    sum(CASE when pday is null THEN 1 ELSE 0 END) as missing,
    ST_x(s.geom) as lon, ST_y(s.geom) as lat from summary_%s c JOIN stations s
    ON (s.iemid = c.iemid)
    WHERE s.network in ('IA_COOP') and s.iemid = c.iemid and
    extract(month from day) = %s and
    extract(year from day) = extract(year from now())
    GROUP by id, lat, lon""" % (now.year, now.strftime("%m"),)

lats = []
lons = []
precip = []
labels = []
icursor.execute(sql)
for row in icursor:
    if row[2] > (now.day / 3):
        continue

    sid = row[0]
    labels.append(sid)
    lats.append(row[4])
    lons.append(row[3])
    precip.append(row[1])


m = MapPlot(title="This Month's Precipitation [inch] (NWS COOP Network)",
            subtitle=now.strftime("%b %Y"), axisbg='white')
m.plot_values(lons, lats, precip, fmt='%.2f', labels=labels)
m.drawcounties()
pqstr = "plot c 000000000000 coopMonthPlot.png bogus png"
m.postprocess(view=False, pqstr=pqstr)
