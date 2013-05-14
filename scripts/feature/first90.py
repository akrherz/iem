import mx.DateTime
import numpy
import iemdb, iemplot
import network
nt = network.Table("IACLIMATE")
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()

lats = []
lons = []
vals = []
ccursor.execute("""
  SELECT station, avg(extract(doy from minday)) from
  (SELECT station, year, min(day) as minday from alldata_ia where high > 89
  and station != 'IA0000' and substr(station,2,1) != 'C'
  GROUP by station, year) as foo GROUP by station
""")
for row in ccursor:
    if not nt.sts.has_key(row[0]):
        continue
    vals.append( row[1] )
    lats.append( nt.sts[row[0]]['lat'] )
    lons.append( nt.sts[row[0]]['lon'] )

labels = []
sts = mx.DateTime.DateTime(2000,1,1)
for i in range(min(vals), max(vals)+4,4):
    ts = sts + mx.DateTime.RelativeDateTime(days=(i-1))
    labels.append( ts.strftime("%b %d") )
    
print labels
cfg = {
    'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': -1,
 'nglSpreadColorEnd'  : 2,
 'cnLevelSelectionMode': 'ManualLevels',
  'cnLevelSpacingF'      : 4.0,
 'cnMinLevelValF'       : min(vals),
 'cnMaxLevelValF'       : max(vals),
 'lbLabelStride'    : 1,
 'lbLabelFontHeightF': 0.0075,
 '_title'             : "Average Date of First 90 Degree Temperature",
 '_valid'             : "based on long term climate data",
  'lbTitleString'      : " ",
  'cnExplicitLabelBarLabelsOn': True,
  'lbLabelStrings': labels,
  
        }

fp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(fp,"","")
iemplot.makefeature(fp)
