"""
OK GRBI4 - Turkey at Garber
OK EKDI4 ?  maybe trib Turkey above French Hollow Creek at Elkader
OK TENI4 ?  Ten Mile Bridge
OK EGNI4 ? Turkey River Elgin
no on river? OK BANI4 or OK ELGI4 - Otter Creek Elgin
CMTI4 Clermont
OK EDRI4 - Turkey River at Eldorado
SPLI4 - Spillville
Bad Data OK TCGI4 - Turkey River at Cresco

SPLI4
EDRI4
CMTI4
TENI4
EKDI4
GRBI4

"""
import pytz
from pyiem.datatypes import distance
import pyproj
import datetime
from PIL import Image
import numpy as np
import psycopg2
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pyiem.plot import MapPlot, nwsprecip
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable

p26915 = pyproj.Proj(init="EPSG:26915")
central = pytz.timezone("America/Chicago")
nt = NetworkTable("IA_DCP")

pgconn = psycopg2.connect(database='hads', host='iemdb-hads', user='nobody')

df = read_sql("""
    SELECT distinct station, valid, key, value from raw2016_08 where
    station in ('SPLI4', 'EDRI4', 'CMTI4', 'TENI4', 'EKDI4', 'GRBI4')
    and valid >= '2016-08-23 23:00+00' and valid < '2016-08-24 23:00+00'
    and substr(key, 1, 2) = 'HG' ORDER by valid ASC
    """, pgconn, index_col=None)
now = df['valid'].min()
maxval = df['valid'].max()
xticks = []
xticklabels = []
while now < maxval:
    xticks.append(now)
    lts = now.astimezone(central)
    fmt = "%-I %p" if lts.hour != 0 else 'Mid\n%b %d'
    xticklabels.append(lts.strftime(fmt))
    now += datetime.timedelta(hours=3)
ax = plt.axes([0.07, 0.35, 0.48, 0.55])
lats = []
lons = []
ids = []
colors = []
delay0 = None
m0 = None
offset0 = None
elev0 = None
names = ['Spillville', 'El Dorado', 'Clermont', 'Elgin (Ten Mile)',
         'Elkader', 'Garber']
stations = ['SPLI4', 'EDRI4', 'CMTI4', 'TENI4', 'EKDI4', 'GRBI4']
for station, name in zip(stations, names):
    lats.append(nt.sts[station]['lat'])
    lons.append(nt.sts[station]['lon'])
    m = p26915(lons[-1], lats[-1])
    if m0 is None:
        m0 = m
    dist = distance(((m[0] - m0[0])**2 + (m[1] - m0[1])**2)**0.5,
                    "M").value("MI")
    ids.append(station)
    df2 = df[df['station'] == station]
    # Find first timestamp over 110% of t0
    idx = df2[df2['value'] > (df2.iloc[0]['value'] * 1.1)].index[0]
    delay = df2.loc[idx]['valid'] - df2.iloc[0]['valid']
    if delay0 is None:
        delay0 = delay
    offset = (delay - delay0).total_seconds() / 3600.
    if offset == 0:
        offset0 = offset
        speed = 0
    else:
        toffset = offset - offset0
        speed = dist / toffset
    elev = nt.sts[station]['elevation']
    if elev0 is None:
        elev0 = elev
    drop = (elev0 - elev)
    elev0 = elev
    if drop == 0:
        slope = 0
    else:
        slope = drop / distance(dist, 'MI').value("M") * 100
    print station, drop, dist, slope, elev
    label = "%s %s %.1fh %.1fmph" % (station, name, offset, speed)
    ln = ax.plot(df2['valid'].values, df2['value'].values, lw=2, label=label)
    colors.append(plt.getp(ln[0], 'c'))

ax.legend(loc=(-0.05, -0.5), ncol=2, fontsize=14)
ax.grid(True)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_ylabel("Stage (ft)")

ax2 = plt.axes([0.57, 0.35, 0.35, 0.55])
cax = plt.axes([0.93, 0.1, 0.06, 0.8])
bufr = 0.2
m = MapPlot(sector='custom', south=(min(lats) - bufr),
            title='23-24 August 2016 Turkey River Gauges',
            subtitle=('Legend shows time delay from initial rise at '
                      'Spillville, overall speed to reach location'),
            north=(max(lats) + bufr), east=(max(lons) + bufr),
            west=(min(lons) - bufr), ax=ax2, cax=cax, axisbg='white',
            caption='Data from Iowa Flood Center, USGS, NWS')

img = Image.open("p24h_201608241200.png")
data = np.flipud(np.asarray(img))
# 7000,3500 == -130,-60,55,25 ===  -100 to -90 then 38 to 45
sample = data[1800:2501, 3000:4501]
sample = np.where(sample == 255, 0, sample)
data = sample * 0.01
data = np.where(sample > 100, 1. + (sample - 100) * 0.05, data)
data = np.where(sample > 180, 5. + (sample - 180) * 0.2, data)
lons2 = np.arange(-100, -84.99, 0.01)
lats2 = np.arange(38, 45.01, 0.01)

x, y = np.meshgrid(lons2, lats2)
clevs = [0.01, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8,
         10]

m.contourf(x[:, :-1], y[:, :-1], data, clevs, cmap=nwsprecip())


for lon, lat, myid, c in zip(lons, lats, ids, colors):
    m.plot_values([lon], [lat], [myid], '%s', color=c, labelbuffer=0,
                  outlinecolor='white')
m.drawcities()
m.drawcounties()
m.ax.text(0.0, -0.1, "MRMS 24 Hour Precip ending 7 AM 24 Aug",
          transform=m.ax.transAxes)

plt.gcf().set_size_inches(10, 5)
plt.gcf().savefig('test.png', figsize=(9, 5))
