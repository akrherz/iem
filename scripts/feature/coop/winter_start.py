import psycopg2
import datetime
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
COOP = psycopg2.connect(database="coop", host='iemdb', user='nobody')
ccursor = COOP.cursor()

nt = NetworkTable("NCDC81")

ccursor.execute("""
    WITH newdates as (
    SELECT station, valid,
    (case when extract(month from valid) < 7 then valid + '366 days'::interval
     else valid end) as newvalid, high, low
    from ncdc_climate81 where substr(station,1,3) = 'USC'),

    movingavgs as (
    SELECT station, valid, newvalid,
    avg((high+low)/2.) OVER (PARTITION by station
    ORDER by newvalid ASC ROWS BETWEEN 91 PRECEDING AND CURRENT ROW) from
    newdates),

    ranks as (
    SELECT station, valid, avg,
    rank() OVER (PARTITION by station ORDER by avg ASC) from movingavgs)

    SELECT station, valid, avg from ranks WHERE rank = 1
""")
lats = []
lons = []
vals = []
for row in ccursor:
    station = row[0]
    if station not in nt.sts:
        continue
    lats.append(nt.sts[station]['lat'])
    lons.append(nt.sts[station]['lon'])
    vals.append(int(row[1].strftime("%j")))

labels = []
sts = datetime.datetime(2000, 1, 1)
ticks = range(47, 74, 2)
for i in ticks:
    ts = sts + datetime.timedelta(days=i)
    labels.append(ts.strftime("%b %d"))

m = MapPlot(sector='conus', axisbg='white',
            title=('End Date of Coldest 91 Day Period '
                   '(End of Winter, Start of Spring)'),
            subtitle='based on NCDC 1981-2010 Climatology of Average(high+low)'
            )
m.contourf(lons, lats, vals, ticks, clevlabels=labels)
m.postprocess(filename='150225.png')
m.close()
