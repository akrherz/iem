from PIL import Image
from pyiem.plot import MapPlot
import numpy as np
import psycopg2
from pyiem.network import Table as NetworkTable
pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = pgconn.cursor()

cursor.execute("""SELECT ST_x(geom) as lon, ST_y(geom) as lat,
max(magnitude) from lsrs_2016
where wfo in ('DMX', 'DVN', 'ARX') and typetext = 'HEAVY RAIN' and
valid > '2016-05-23' GROUP by lon, lat ORDER by max DESC""")
llons = []
llats = []
vals = []
for row in cursor:
    llons.append(row[0])
    llats.append(row[1])
    vals.append("%.2f" % (row[2], ))


img = Image.open("p24h_201605240000.png")
data = np.flipud(np.asarray(img))
# 7000,3500 == -130,-60,55,25 ===  -100 to -90 then 38 to 45
sample = data[1800:2501, 3000:4501]
sample = np.where(sample == 255, 0, sample)
data = sample * 0.01
data = np.where(sample > 100, 1. + (sample - 100) * 0.05, data)
data = np.where(sample > 180, 5. + (sample - 180) * 0.2, data)
lons = np.arange(-100, -84.99, 0.01)
lats = np.arange(38, 45.01, 0.01)

x, y = np.meshgrid(lons, lats)

buff = 0.5
m = MapPlot(sector='custom', west=min(llons)-buff,
            east=max(llons)+buff, south=min(llats)-buff,
            north=max(llats)+buff,
            title='NOAA MRMS 24 Hour RADAR-Only Precipitation Estimate',
            subtitle=("MRMS valid 7 PM 22 May 2016 to 7 PM 23 May 2016, "
                      "NWS Local Storm Reports Overlaid"))
clevs = np.arange(0, 0.2, 0.05)
clevs = np.append(clevs, np.arange(0.2, 1.0, 0.1))
clevs = np.append(clevs, np.arange(1.0, 5.0, 0.25))
clevs = np.append(clevs, np.arange(5.0, 10.0, 1.0))
clevs[0] = 0.01
m.contourf(x[:, :-1], y[:, :-1], data, clevs)

nt = NetworkTable("IA_ASOS")
lo = []
la = []
va = []
for sid in nt.sts.keys():
    lo.append(nt.sts[sid]['lon'])
    la.append(nt.sts[sid]['lat'])
    va.append(nt.sts[sid]['name'])

# m.plot_values(lo, la, va, fmt='%s', textsize=10, color='black')
m.plot_values(llons, llats, vals, fmt='%s')
m.drawcities()

m.map.drawcounties(zorder=10, linewidth=1.)


m.postprocess(filename='test.png')
