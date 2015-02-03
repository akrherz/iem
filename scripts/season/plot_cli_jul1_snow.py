import psycopg2
import datetime

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()



cursor.execute("""
 select station, st_x(geom), st_y(geom), snow_jul1 
 from cli_data c JOIN stations t on (t.id = c.station) 
 WHERE c.valid = 'YESTERDAY' and t.network = 'NWSCLI' and snow_jul1 is not null
""")
lats = []
lons = []
vals = []

for row in cursor:
    stid = row[0][-3:]
    if stid in ['RAP', 'DVN', 'FGF', 'OAX', 'MPX']:
        continue
    lats.append(row[2])
    lons.append(row[1])
    vals.append(row[3])

from pyiem.plot import MapPlot

yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
year = yesterday.year if yesterday.month > 6 else yesterday.year - 1

m = MapPlot(sector='midwest', axisbg='white',
       title='NWS Total Snowfall (inches) thru %s' % (
                                    yesterday.strftime("%-d %B %Y"),),
       subtitle= '1 July %s - %s' % (year, 
                datetime.datetime.today().strftime("%-d %B %Y"),))
m.plot_values(lons, lats, vals, fmt='%.1f')
pqstr = "data ac %s0000 summary/mw_season_snowfall.png mw_season_snowfall.png png" % (
        datetime.datetime.today().strftime("%Y%m%d"),)
m.postprocess(view=False, pqstr=pqstr)
