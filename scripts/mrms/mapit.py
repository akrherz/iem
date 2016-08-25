from PIL import Image
from pyiem.plot import MapPlot, nwsprecip
import numpy as np
import psycopg2
from pyiem.network import Table as NetworkTable
pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor()

cursor.execute("""SELECT ST_x(geom) as lon, ST_y(geom) as lat,
pday from summary_2016 s JOIN stations t on (s.iemid = t.iemid)
where day = '2016-08-24' and network in ('WI_COOP', 'MN_COOP', 'IA_COOP')
and pday > 0 ORDER by pday DESC""")
llons = []
llats = []
vals = []
for row in cursor:
    llons.append(row[0])
    llats.append(row[1])
    vals.append("%.2f" % (row[2], ))

pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = pgconn.cursor()

cursor.execute("""SELECT ST_x(geom) as lon, ST_y(geom) as lat,
max(magnitude) from lsrs_2016
where wfo in ('DMX', 'DVN', 'ARX') and typetext = 'HEAVY RAIN' and
valid > '2016-08-23' GROUP by lon, lat ORDER by max DESC""")
for row in cursor:
    llons.append(row[0])
    llats.append(row[1])
    vals.append("%.2f" % (row[2], ))


img = Image.open("p24h_201608241200.png")
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
m = MapPlot(sector='custom', projection='aea', west=-93.2,
            east=-90.3, south=42.5,
            north=44.,
            title='NOAA MRMS 24 Hour RADAR-Only Precipitation Estimate',
            subtitle=("MRMS valid 7 AM 23 Aug 2016 to 7 AM 24 Aug 2016, "
                      "NWS Local Storm + COOP Reports Overlaid"))
clevs = [0.01, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8,
         10]

m.contourf(x[:, :-1], y[:, :-1], data, clevs, cmap=nwsprecip())

nt = NetworkTable("IA_ASOS")
lo = []
la = []
va = []
for sid in nt.sts.keys():
    lo.append(nt.sts[sid]['lon'])
    la.append(nt.sts[sid]['lat'])
    va.append(nt.sts[sid]['name'])

# m.plot_values(lo, la, va, fmt='%s', textsize=10, color='black')
m.map.drawcounties(zorder=4, linewidth=1.)
m.drawcities(labelbuffer=25, textsize=10, color='white',
             outlinecolor='#000000')
m.textmask[:, :] = 0
m.plot_values(llons, llats, vals, fmt='%s', labelbuffer=5)



m.postprocess(filename='test.png')
