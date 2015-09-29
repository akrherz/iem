import mx.DateTime
import numpy
import psycopg2
COOP = psycopg2.connect(database="coop", host='iemdb', user='nobody')
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

lats = []
lons = []
vals = []
ccursor.execute("""
    SELECT distinct id, x(geom), y(geom) from stations
    WHERE network ~* 'CLIMATE' and network not in ('HICLIMATE',
    'AKCLIMATE') and network in ('IACLIMATE', 'MNCLIMATE', 'NDCLIMATE', 'SDCLIMATE',
 'NECLIMATE', 'KSCLIMATE', 'MOCLIMATE', 'KYCLIMATE', 'ILCLIMATE', 'WICLIMATE',
 'INCLIMATE', 'OHCLIMATE', 'MICLIMATE')
""")
for row in ccursor:

    stid = row[0]
    # Query out the data
    data = numpy.zeros( (366*2) )
    data[:] = 100.
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
    pos = 0

    for i in range(0,367):
        val = numpy.average(data[i:i+91])
        #print i, val
        if val < minv:
            minv = val
            pos = i

    if pos < 100:
        print stid, pos, minv
        pos += 366
        
    if pos > (365+15): #APR 15
        print stid, pos, minv, 'SKIP'
        continue
    vals.append( pos + 1 + 91) # Spring
    lats.append( row[2] )
    lons.append( row[1] )

labels = []
sts = mx.DateTime.DateTime(2000,1,1)
for i in range(min(vals), max(vals)+4,4):
    ts = sts + mx.DateTime.RelativeDateTime(days=(i-1))
    labels.append( ts.strftime("%b %d") )
    
print labels
cfg = {
    '_midwest':   True,
    'wkColorMap': 'BlAqGrYeOrRe',
     'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 'cnLevelSelectionMode': 'ManualLevels',
  'cnLevelSpacingF'      : 4.0,
 'cnMinLevelValF'       : min(vals),
 'cnMaxLevelValF'       : max(vals),
 'lbLabelStride'    : 1,
 'lbLabelFontHeightF': 0.012,
 '_title'             : "When does Spring start? End Date of Coldest 91 Day Period",
 '_valid'             : "based on NCDC 1971-2000 Climatology Avg(high+low)",
  'lbTitleString'      : "  ",
  'cnExplicitLabelBarLabelsOn': True,
  'lbLabelStrings': labels,
  
        }

fp = iemplot.simple_contour(lons, lats, vals, cfg)
#iemplot.postprocess(fp,"","")
iemplot.makefeature(fp)
