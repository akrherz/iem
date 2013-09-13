import psycopg2
import network
from pyiem.plot import MapPlot
from matplotlib.patches import Polygon
import numpy as np


nt = network.Table("IACLIMATE")

COOP = psycopg2.connect(database='coop', user='nobody', host='iemdb')
cursor = COOP.cursor()

cnts = {}
for days in [30,60,90,120]:
#for days in [30,]:
    cursor.execute("""
 select station, (max(case when year = 2013 then sum else 0 end) - avg(sum)) 
 / stddev(sum) as sigma from 
   (select station, year, sum(precip) from alldata_ia where 
    sday between to_char(('2013-09-12'::date - '%s days'::interval), 'mmdd') 
    and to_char(('2013-09-12'::date), 'mmdd') and year > 1950 and 
    station in (select id from stations where network = 'IACLIMATE') 
    GROUP by station, year ) as foo GROUP by station ORDER by sigma
    """ % (days,))
    
    for row in cursor:
        if not cnts.has_key( row[0] ):
            cnts[ row[0] ] = 0
        if row[0] == 'IA5086':
            print days, row
        cnts[ row[0] ] += 1 if row[1] < -1.2 else 0
        
hole = [(-90.77660074466883, 42.71011495592424), 
        (-90.618964082141, 42.713089232575705), 
        (-90.40184188658382, 42.683346466061025), 
        (-90.24717950070747, 42.638732316289), 
        (-90.15497692451196, 42.56437540000229), 
        (-90.14902837120901, 42.5167869735788), 
        (-90.25907660731335, 42.49299276036705), 
        (-90.39291905662941, 42.43945578064062), 
        (-90.59219559227779, 42.38889307756566), 
        (-90.77660074466883, 42.36509886435392), 
        (-90.92531457724223, 42.33238182118777), 
        (-91.07997696311858, 42.32345899123336), 
        (-91.24058790229788, 42.30263905467309), 
        (-91.46068437450653, 42.299664778021615), 
        (-91.52611846083883, 42.31156188462749), 
        (-91.603449653777, 42.341304651142174), 
        (-91.62129531368582, 42.36509886435392), 
        (-91.62129531368582 ,42.40673873747447), 
        (-91.59155254717113, 42.4513528872465), 
        (-91.55883550400499, 42.51381269692733), 
        (-91.46960720446093, 42.56437540000229), 
        (-91.40417311812863, 42.620886656380186), 
        (-91.21381941243466, 42.65657797619781), 
        (-91.05023419660391, 42.683346466061025), 
        (-90.92531457724223, 42.69821784931837), 
        (-90.77660074466883, 42.71011495592424)]
hole = np.array(hole)

lons = []
lats = []
vals = []
for key in cnts.keys():
    if key[2] == 'C' or key == 'IA0000':
        continue
    
    lons.append( nt.sts[key]['lon'] )
    lats.append( nt.sts[key]['lat'] )
    vals.append( cnts[key] )

m = MapPlot(sector='iowa', title='10 Sept 2013 US Drought Monitor',
            subtitle=r"Count of 30 / 60 / 90 / 120 Day Standardized Precip Index below -1.2 (D2+) $\sigma$")
m.plot_values(lons, lats, vals, textsize=18)

colors = ['#f6eb13', '#ffcc66', '#ff9900', '#ff3333', '#FF00FF']
classes = ['D0: Abnormal', 'D1: Moderate', 'D2: Severe']
m.map.readshapefile('dm_current', 'dm', ax=m.ax)
for nshape, seg in enumerate(m.map.dm):
    cat = m.map.dm_info[nshape]['DM']
    poly=Polygon(seg, fc=colors[cat], ec='k', lw=.4, zorder=3)
    m.ax.add_patch(poly)

x,y = m.map(hole[:,0], hole[:,1])
poly=Polygon(zip(x,y), fc='w', ec='k', lw=.4, zorder=3)
m.ax.add_patch(poly)

for i in range(len(classes)):
    m.fig.text(0.9, 0.91 + ((i*2.5) /100.0), "%s" % (classes[i],),
                          ha='right', color=colors[i], fontsize=14)

m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')