
import iemdb, iemplot
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

data = {}
ccursor.execute("""
    SELECT station, x(geom) as lon, y(geom) as lat, high from ncdc_climate71 c,
    stations s WHERE lower(s.id) = c.station and valid = '2000-09-03'
    and x(geom) between -120 and -60 and y(geom) between 20 and 52
""" )

for row in ccursor:
    data[row[0]] = row

ccursor.execute("""
    SELECT station, high from ncdc_climate71 c
     WHERE valid = '2000-09-24'
""" )

lats = []
lons = []
vals = []
for row in ccursor:
    if not data.has_key(row[0]):
        print 'What', row[0]
        continue
    vals.append( row[1] - data[row[0]][3] )
    lats.append( data[row[0]][2] )
    lons.append( data[row[0]][1] )
print min(lats), max(lats)
print min(lons), max(lons)
cfg = {
    '_conus':   True,
 '_title'             : "Three Week Change in High Temperature Climatology",
 '_valid'             : "03 September - 24 September",
  'lbTitleString'      : "[F]",
        }

fp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.postprocess(fp,"","")