import mx.DateTime
import numpy
import iemdb, iemplot
COOP = iemdb.connect("coop", bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

lats = []
lons = []
vals = []
ccursor.execute("""
    SELECT distinct id, x(geom), y(geom) from stations
    WHERE network ~* 'CLIMATE' and network not in ('HICLIMATE',
    'AKCLIMATE')
""")
for row in ccursor:

    stid = row[0]
    # Query out the data
    data = numpy.zeros( (366*2) )
    #data[:] = 100.
    ccursor2.execute("""
    select valid, high from ncdc_climate71 where 
    station = %s ORDER by valid ASC
    """, (stid.lower(),))
    i= 0
    for row2 in ccursor2:
        data[i] = row2[1]
        data[i+366] = row2[1]
        i += 1
    if i == 0:
        continue
    minv = 100.
    maxv = 0.

    for i in range(0,367):
        val = numpy.average(data[i:i+91])
        if val < minv:
            minv = val
            minpos = i
        if val > maxv:
            maxv = val
            maxpos = i

    if minpos < 100:
        #print stid, pos, minv
        pos += 366
    vals.append( minpos - maxpos - 91)
    lats.append( row[2] )
    lons.append( row[1] )

labels = []
sts = mx.DateTime.DateTime(2000,1,1)
for i in range(320,370,4):
    ts = sts + mx.DateTime.RelativeDateTime(days=(i-1))
    labels.append( ts.strftime("%b %d") )
    
#print labels
cfg = {
    '_conus':   True,
    'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
# 'cnLevelSelectionMode': 'ManualLevels',
#  'cnLevelSpacingF'      : 4.0,
# 'cnMinLevelValF'       : 320.0,
# 'cnMaxLevelValF'       : 368.0,
# 'lbLabelStride'    : 1,
# 'lbLabelFontHeightF': 0.012,
'tiMainFontHeightF': 0.02,
 '_title'             : "Fall Season Duration. Days between warmest and Coolest 91 day period. ",
 '_valid'             : "based on NCDC 1971-2000 Climatology Avg(high+low)",
  'lbTitleString'      : "days",
 # 'cnExplicitLabelBarLabelsOn': True,
 # 'lbLabelStrings': labels,
  
        }

fp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(fp,"","")
iemplot.makefeature(fp)
