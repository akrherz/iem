#!/mesonet/python/bin/python
# Generate fancy plot of 4 inch soil temperatures per county...

import Ngl, Numeric, mx.DateTime, os, sys
from pyIEM import iemdb, stationTable
st = stationTable.stationTable("/mesonet/TABLES/campbellDB.stns")
i = iemdb.iemdb()
isuag = i['isuag']
postgis = i['postgis']
day_ago = int(sys.argv[1])
ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=day_ago)

# Query out the data
soil_obs = []
lats = []
lons = []
rs = isuag.query("SELECT station, c30 from daily WHERE \
     valid = '%s' and c30 > 0" % (ts.strftime("%Y-%m-%d"), ) ).dictresult()
for i in range(len(rs)):
  stid = rs[i]['station']
  soil_obs.append( rs[i]['c30'] )
  lats.append( st.sts[stid]['lat'] )
  lons.append( st.sts[stid]['lon'] )


def sampler(xaxis, yaxis, vals, x, y):
  i = 0
  while (xaxis[i] < x):
    i += 1
  j = 0
  while (yaxis[j] < y):
    j += 1
  return vals[i,j]

# Grid it
numxout = 40
numyout = 40
xmin    = min(lons) - 1.
ymin    = min(lats) - 1.
xmax    = max(lons) + 1.
ymax    = max(lats) + 1.
xc      = (xmax-xmin)/(numxout-1)
yc      = (ymax-ymin)/(numyout-1)

xo = xmin + xc*Numeric.arange(0,numxout)
yo = ymin + yc*Numeric.arange(0,numyout)

analysis = Ngl.natgrid(lons, lats, soil_obs, list(xo), list(yo))

# Generate plot
rlist = Ngl.Resources()
rlist.wkColorMap = "BlAqGrYeOrRe"

wks = Ngl.open_wks( "ps","highs",rlist)
resources = Ngl.Resources()

resources.nglDraw     = False
resources.nglFrame    = False

resources.cnFillOn              = True     # Turn on contour fill.
resources.cnInfoLabelOn         = False    # Turn off info label.
resources.cnLineLabelsOn        = False    # Turn off line labels.
resources.cnLinesOn        = False    # Turn off line labels.

resources.lbOrientation         = "Horizontal" 
resources.tiMainString          = "Iowa 4in Soil Temperatures %s" % (ts.strftime("%b %d %Y"), )

resources.cnMinLevelValF = 10
resources.cnMaxLevelValF = 100
resources.cnLevelSpacingF = 5
resources.cnLevelSelectionMode = "ManualLevels"



resources.lbTitleString = "[Fahrenheit]"
resources.lbOrientation = "Horizontal"

# turn off grid
resources.pmTickMarkDisplayMode = "Never"

resources.nglPaperOrientation = "portrait"


resources.sfXCStartV = min(xo)
resources.sfXCEndV   = max(xo)
resources.sfYCStartV = min(yo)
resources.sfYCEndV   = max(yo)

resources.mpProjection = "LambertEqualArea"  # Change the map projection.
resources.mpCenterLonF = -95.
resources.mpCenterLatF = 42.

resources.mpLimitMode = "LatLon"    # Limit the map view.
resources.mpMinLonF   = -96.6
resources.mpMaxLonF   = -90.
resources.mpMinLatF   = 40.
resources.mpMaxLatF   = 44.
resources.mpPerimOn   = False
resources.pmTickMarkDisplayMode = "Never"
resources.mpOutlineBoundarySets     = "AllBoundaries"
resources.mpDataBaseVersion         = "mediumres"
resources.mpDataSetName             = "Earth..2"
resources.mpGridAndLimbOn = False
resources.mpUSStateLineThicknessF = 3

resources.mpFillOn              = True 
resources.mpFillAreaSpecifiers  = ["Conterminous US",]
resources.mpSpecifiedFillColors = [0,]
resources.mpAreaMaskingOn       = True
resources.mpMaskAreaSpecifiers = ["Conterminous US : Iowa",]
resources.cnFillDrawOrder       = "Predraw" 

analysis2 = Numeric.transpose(analysis)
contour = Ngl.contour_map(wks,analysis2,resources)

# Draw text!
txres               = Ngl.Resources()
txres.txFontHeightF = 0.02
txres.txFont        = "helvetica-bold"

# Query out centroids of counties...
rs = postgis.query("SELECT x(centroid(the_geom)) as lon, \
  y(centroid(the_geom)) as lat \
 from uscounties WHERE state_name = 'Iowa'").dictresult()
for i in range(len(rs)):
  lat = rs[i]['lat']
  lon = rs[i]['lon']
  smp = sampler(xo,yo,analysis, lon, lat)

  text = Ngl.add_text(wks,contour,"%.0f" % (smp,),lon,lat,txres)

Ngl.panel(wks,[contour,],[1,1])


 
Ngl.end()

os.system("convert -trim  highs.ps obs.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 soilt_day%s.png bogus png' obs.png" % (day_ago,) )
