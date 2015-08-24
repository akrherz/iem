import iemdb
import numpy
import iemplot
import sys
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()

def fetch():
    data = open('days77sep.txt', 'w')
    for yr in range(1973,2012):
        print yr
        acursor.execute("""
 SELECT station, extract(year from d) as yr, sum(case when cnt > 0 then 1 else 0 end) from 
 (SELECT station, date(valid) as d, sum(case when dwpf >= 77 then 1 else 0 end) as cnt 
  from t%s WHERE extract(month from valid) = 9 GROUP by station, d) as foo 
 GROUP by station, yr
        """ % (yr,))

        for row in acursor:
            data.write("%s,%s,%s\n" % row)
    
    data.close()
    
#fetch()
#sys.exit()
data8099 = {}
data0011 = {}
firstob = {}
for line in open('days77aug.txt'):
    tokens = line.split(",")
    yr = float(tokens[1])
    if not data8099.has_key(tokens[0]):
        data8099[tokens[0]] = []
        data0011[tokens[0]] = []
        firstob[tokens[0]] = 2011
    if yr >= 1980 and yr < 2000:
        data8099[tokens[0]].append( float(tokens[2]) )
    elif yr >= 2000:
        data0011[tokens[0]].append( float(tokens[2]) )
        
    if yr < firstob[tokens[0]]:
        firstob[tokens[0]] = yr
        
    
stations = {}
mcursor.execute("""
 SELECT id, x(geom), y(geom) from stations where network ~* 'ASOS' or network = 'AWOS'
""")
for row in mcursor:
    stations[row[0]] = {'lat': row[2], 'lon': row[1]}

vals = []
lats = []
lons = []    
for sid in data8099.keys():
    if not stations.has_key(sid):
        continue
    
    year1 = firstob[sid]
    if year1 > 1980:
        continue

    ar8099 = numpy.array( data8099[sid] ) 
    ar0011 = numpy.array( data0011[sid] )
    diff = (numpy.sum(ar0011) / 12.0) -  (numpy.sum(ar8099) / 20.0)
    if diff < -10 or diff > 10:
        continue
    lats.append( stations[sid]['lat'] )
    lons.append( stations[sid]['lon'] )
    vals.append( diff )

vals = numpy.array( vals )
maxV = int(max( numpy.max(vals), 0 - numpy.min(vals))) + 1

cfg = {
       '_title': 'August Change in Average Number of Days per Year AOB 77F Dew Point',
       'lbTitleString': 'days',
       '_valid' : 'Period of 2000-2011 minus Period of 1980-1999',
       #'_conus': True,
       '_midwest': True,
        'cnLevelSelectionMode' : 'ManualLevels',
 'cnLevelSpacingF'      : 2.0,
 'cnMinLevelValF'       : - maxV,
 'cnMaxLevelValF'       : maxV,
  'wkColorMap'         : 'BlWhRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 '_MaskZero': True,
 '_showvalues'        : True,
 '_format' : '%.1f',

       }
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(tmpfp, None, fname='aug_77_change_mw.png')