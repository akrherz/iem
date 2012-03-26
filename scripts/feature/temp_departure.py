import mx.DateTime
import numpy
import iemdb, iemplot
COOP = iemdb.connect("coop", bypass=True)
MESOSITE = iemdb.connect("mesosite", bypass=True)
IEM = iemdb.connect("iem", bypass=True)
mcursor = MESOSITE.cursor()
ccursor = COOP.cursor()
icursor = IEM.cursor()

climate = {}
ccursor.execute("""
	SELECT station, high from ncdc_climate71 where valid = '2000-03-21'
""")
for row in ccursor:
    climate[ row[0].lower() ] = row[1]

xref = {}
mcursor.execute("""
    SELECT id, climate_site from stations
    WHERE network ~* 'ASOS' and climate_site is not null
""")
for row in mcursor:
    xref[ row[0] ] = row[1].lower()

icursor.execute("""
	SELECT t.id, x(geom), y(geom), max_tmpf, t.state from summary_2012 s JOIN stations t on (t.iemid = s.iemid) and 
      	day = '2012-03-21' and t.network ~* 'ASOS' and max_tmpf > -40 and
        max_tmpf < 100 and t.id not in ('SQI') and 
	t.network not in ('AK_ASOS','HI_ASOS') and t.country = 'US'
""")
vals = []
lons = []
lats = []
for row in icursor:
    stid = row[0]
    if not xref.has_key(stid):
        continue
    csite = xref[stid]
    if not climate.has_key(csite):
        continue
    if row[4] == 'ND':
        print row
    chigh = climate[csite]

    vals.append( row[3] - chigh )
    lats.append( row[2] )
    lons.append( row[1] )

cfg = {
    '_conus':   True,
    'wkColorMap': 'ViBlGrWhYeOrRe',
     'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 'cnLevelSelectionMode': 'ManualLevels',
  'cnLevelSpacingF'      : 15.0,
 'cnMinLevelValF'       : -60.0,
 'cnMaxLevelValF'       : 60.0,
# 'lbLabelStride'    : 1,
# 'lbLabelFontHeightF': 0.012,
 '_title'             : "High Temperature Departure from 1981-2010 Average",
 '_valid'             : " 21 Mar 2011",
  'lbTitleString'      : "F",
#  'cnExplicitLabelBarLabelsOn': True,
#  'lbLabelStrings': labels,
  
        }

fp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(fp,"","")
iemplot.makefeature(fp)
