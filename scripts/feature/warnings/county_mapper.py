import matplotlib.colors as mpcolors
import matplotlib.cm as cm
import psycopg2
import datetime
import subprocess

from pyiem.plot import MapPlot
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

opts = {'subtitle': "In Tornado, SVR, or Flash Flood Warnings",
        'sdate': datetime.date(1997, 1, 1),
        'edate': datetime.date(2015, 1, 1),
        'normalized': True,
        'dbcols': ('TO', 'SV', 'FF')
        }
opts['title'] = "Yearly Average Minutes"
opts['years'] = float(opts['edate'].year - opts['sdate'].year)
opts['units'] = 'minutes per year'
# bins = [1,2,5,10,15,20,25,30,45,60,75,90,120,150,180,240]
# bins = [1, 10, 30, 45, 60, 90, 120, 180, 240, 300, 360, 480, 600, 720, 840]
bins = [1, 30, 60, 120, 240, 360, 480, 600, 840, 1080, 1320, 1540, 1760]
# bins = [0.01,0.1,0.25,0.5,0.75,1,2,3,4,5,7,10,15]
# bins = [0.1,1,2,5,7,10,15,20,25,30,40,50,60,70,80]

if opts['normalized']:
    opts['title'] += " (Normalized by County Size)"
    opts['units'] += " / sq km"
    # bins = [0.0001, 0.0002, 0.0005, 0.0007, 0.001, 0.0015, 0.002, 0.006,
    #        0.01, 0.012, 0.015, 0.02, 0.025]
    bins = [0.001, 0.003, 0.005, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8]

fn = "%s_%s_%s_%s.png" % (opts['sdate'].year, opts['edate'].year,
                          "-".join(opts['dbcols']),
                          'normalized' if opts['normalized'] else 'count')

# bins = [0.001, 0.003, 0.005, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8]
# bins = [1,2,3,4,5,6,7,8,9,10,15,20,30,50,100,125]
# bins = [0.02,0.5, 1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 16, 20, 24, 30]
# bins = [1,2,5,10,15,20,25,30,45,60,75,90,120,150,180,240]
# bins = [1,2,3,4,5,7,10,15,20,25,30,35,40,50,75,100]


cmap = cm.get_cmap("jet")
cmap.set_under("#ffffff")
cmap.set_over("#000000")

m = MapPlot(sector='nws', axisbg='#EEEEEE',
            title=opts['title'],
            subtitle=('%s, period: %s thru %s'
                      ) % (opts['subtitle'],
                           opts['sdate'].strftime("%-d %b %Y"),
                           opts['edate'].strftime("%-d %b %Y")),
            cwas=True, nostates=True)

norm = mpcolors.BoundaryNorm(bins, cmap.N)

'''
 WITH data as (
  SELECT ugc, count(*) / %s  as data from warnings
  WHERE ugc is not null and
  significance = 'W' and phenomena in %s and issue > %s and issue < %s
  GROUP by ugc),
 u as (SELECT ugc, ST_Area(ST_Transform(geom, 2163)) / 1000000. as area
 from ugcs where substr(ugc,3,1) = 'C' and end_ts is null)

 SELECT data.ugc, data.data, data.data / u.area
 from data JOIN u on (u.ugc = data.ugc)
'''

pcursor.execute("""
WITH data as (
SELECT ugc, count(*) / %s  as data from
 (select distinct ugc, generate_series(issue, expire, '1 minute'::interval)
 from warnings where phenomena in %s and significance = 'W'
 and ugc is not null and (expire - issue) < '1440 minutes'::interval
 and issue > %s and issue < %s) as foo2
 GROUP by ugc),

 u as (SELECT ugc, ST_Area(ST_Transform(geom, 2163)) / 1000000. as area
 from ugcs where substr(ugc,3,1) = 'C' and end_ts is null)

 SELECT data.ugc, data.data, data.data / u.area
 from data JOIN u on (u.ugc = data.ugc)
""", (opts['years'], opts['dbcols'], opts['sdate'], opts['edate']))
data = {}
for row in pcursor:
    data[row[0]] = float(row[2 if opts['normalized'] else 1])

m.fill_ugc_counties(data, bins, cmap=cmap, units=opts['units'])
m.postprocess(filename=fn)
subprocess.call("xv %s" % (fn,), shell=True)
