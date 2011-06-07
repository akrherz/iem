import iemdb
import random
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()
import iemplot

sts = {}
mcursor.execute(""" 
SELECT id, x(geom) as lon, y(geom) as lat, network from stations
WHERE (network ~* 'ASOS' or network = 'AWOS') 
and network not in ('IQ_ASOS','AK_ASOS','HI_ASOS','PO_ASOS', 'GU_ASOS')  """)
for row in mcursor:
    sts[ row[0] ] = {'lat': row[2], 'lon': row[1], 'network': row[3]}

acursor.execute("""
    SELECT station, min(wcht(tmpf::numeric,sknt::numeric)) from t2011
    WHERE valid > '2011-02-01' and tmpf > -50 and 
    sknt >= 0 and station != 'MIS' GROUP by station ORDER by min ASC
""")
lats = []
lons = []
data = []
for row in acursor:
    if not sts.has_key(row[0]):
        continue
    #if sts[row[0]]['network'] in ('SD_ASOS','NE_ASOS'):
    #    print row[1], row[0]
    if row[1] > 25 and sts[row[0]]['lat'] > 40 and sts[row[0]]['lat'] < 48  and sts[row[0]]['lon'] < -100 and sts[row[0]]['lon'] > -120:
        print row[1], row[0] 
    data.append( row[1] )
    lats.append( sts[row[0]]['lat'] + (random.random() *.01))
    lons.append( sts[row[0]]['lon'] )
    
cfg = {
       '_conus': True,
       'lbTitleString': '[F]',
       '_title': '1-3 February 2011 Minimum Wind Chill'
       #'_showvalues': True,
       #'_format': '%.0f',
       }

fp = iemplot.simple_contour(lons, lats, data, cfg)
#iemplot.postprocess(fp,'','')
iemplot.makefeature(fp)