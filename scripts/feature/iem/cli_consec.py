"""Consecutative days """
import psycopg2
import datetime
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
nt = NetworkTable("NWSCLI")
PGCONN = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = PGCONN.cursor()

cursor.execute("""
 with obs as (
  select station, valid,
  (case when high > high_normal then 1 else 0 end) as hit from cli_data
  where high is not null and high_normal is not null
  and valid > '2014-09-01'),

  totals as (
  SELECT station,
  max(case when hit = 0 then valid else '2014-09-01'::date end) as last_below,
  max(case when hit = 1 then valid else '2014-09-01'::date end) as last_above,
  count(*) as count from obs GROUP by station)

  SELECT station, last_below, last_above from totals where count > 165
  ORDER by least(last_below, last_above) ASC
""")

lats = []
lons = []
vals = []
colors = []
labels = []

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

for row in cursor:
    if row[0] not in nt.sts:
        continue
    lats.append(nt.sts[row[0]]['lat'])
    lons.append(nt.sts[row[0]]['lon'])
    last_above = row[2]
    last_below = row[1]
    days = 0 - (last_below - last_above).days
    if last_above in [today, yesterday]:
        days = (last_above - last_below).days
    vals.append(days)
    colors.append('r' if days > 0 else 'b')
    labels.append(row[0])

m = MapPlot(sector='conus', axisbg='tan', statecolor='#EEEEEE',
            title='Consecutive Days with High Temp above(+)/below(-) Average',
            subtitle=('based on NWS CLI Sites, map approximately valid for %s'
                      '') % (today.strftime("%-d %b %Y"), ))
m.plot_values(lons, lats, vals, color=colors, labels=labels,
              labeltextsize=8, textsize=12)
m.postprocess(filename='150220.png')
m.close()
