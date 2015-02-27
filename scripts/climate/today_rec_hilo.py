# Generate a map of today's record high and low temperature
from pyiem.plot import MapPlot

import datetime
now = datetime.datetime.now()

from pyiem.network import Table as NetworkTable
nt = NetworkTable('IACLIMATE')
nt.sts["IA0200"]["lon"] = -93.6
nt.sts["IA5992"]["lat"] = 41.65
import psycopg2.extras
coop = psycopg2.connect(database='coop', host='iemdb', user='nobody')

# Compute normal from the climate database
sql = """SELECT station, max_high, min_low from climate WHERE valid = '2000-%s'
    and substr(station,0,3) = 'IA'""" % (now.strftime("%m-%d"),)

obs = []
c = coop.cursor(cursor_factory=psycopg2.extras.DictCursor)
c.execute(sql)
for row in c:
    sid = row['station']
    if sid[2] == 'C' or sid[2:] == '0000' or sid not in nt.sts:
        continue
    obs.append(dict(id=sid[2:], lat=nt.sts[sid]['lat'],
                    lon=nt.sts[sid]['lon'], tmpf=row['max_high'],
                    dwpf=row['min_low']))

m = MapPlot(title="Record High + Low Temperature [F] (1893-%s)" % (now.year,),
            subtitle="For Date: %s" % (now.strftime("%d %b"),),
            axisbg='white')
m.drawcounties()
m.plot_station(obs)
pqstr = ("plot ac %s0000 climate/iowa_today_rec_hilo_pt.png coop_rec_temp.png "
         "png") % (now.strftime("%Y%m%d"), )
m.postprocess(view=False, pqstr=pqstr)
m.close()
