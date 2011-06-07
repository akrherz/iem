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
	SELECT station, high from ncdc_climate71 where valid = '2000-03-17'
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
	SELECT station, x(geom), y(geom), max_tmpf from summary_2011 WHERE
      	day = 'TODAY' and network ~* 'ASOS' and max_tmpf > -40 and
	network not in ('AK_ASOS','HI_ASOS') and station not in ('MWM','FYV')
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
    chigh = climate[csite]

    vals.append( row[3] - chigh )
    lats.append( row[2] )
    lons.append( row[1] )

cfg = {
    '_conus':   True,
    'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
# 'cnLevelSelectionMode': 'ManualLevels',
#  'cnLevelSpacingF'      : 4.0,
# 'cnMinLevelValF'       : 360.0,
# 'cnMaxLevelValF'       : 408.0,
# 'lbLabelStride'    : 1,
# 'lbLabelFontHeightF': 0.012,
'tiMainFontHeightF': 0.02,
 '_title'             : "High Temperature Departure ",
 '_valid'             : " 17 Mar 2011",
  'lbTitleString'      : "F",
#  'cnExplicitLabelBarLabelsOn': True,
#  'lbLabelStrings': labels,
  
        }

fp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(fp,"","")
iemplot.makefeature(fp)
