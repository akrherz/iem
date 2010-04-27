#!/mesonet/python/bin/python

import Ngl
import numpy
import re
import os
import mx.DateTime
from pyIEM import stationTable, iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()

def nine_smooth2D( ar ):
    shp = ar.shape
    nar = numpy.zeros( numpy.shape(ar), numpy.float32)
    for x in range(shp[0]):
        for y in range(shp[1]):
            if (x < 2 or x > shp[0] - 3):
                nar[x,y] = ar[x,y]
                continue 
            if (y < 2 or y > shp[1] - 3):
                nar[x,y] = ar[x,y]
                continue
            nar[x,y] = (numpy.sum(ar[x-2:x+3,y]) + numpy.sum(ar[x,y-2:y+3]))/10.0
    return nar

vsby = []
lats = []
lons = []

sql = "select station, x(geom), y(geom), vsby from current WHERE vsby >= 0 and valid + '2 hours'::interval > now() and network !~* 'RWIS'" 
rs = iemdb.query(sql).dictresult()

for i in range(len(rs)):
    stid = rs[i]['station']
    vsby.append( rs[i]['vsby'] )
    lats.append( rs[i]['y'] )
    lons.append( rs[i]['x'] )

numxout = 140
numyout = 140
xmin    = min(lons)
ymin    = min(lats)
xmax    = max(lons)
ymax    = max(lats)

xc      = (xmax-xmin)/(numxout-1)
yc      = (ymax-ymin)/(numyout-1)

xo = xmin + xc*numpy.arange(0,numxout)
yo = ymin + yc*numpy.arange(0,numyout)
vsby = Ngl.natgrid(lons, lats, vsby, xo, yo)
vsby = nine_smooth2D(vsby)
#print prec

cmap = ["white", "black", "white",
   "Tan2","Tan3","Tan4",
   "SpringGreen2", "SpringGreen3", "SpringGreen4",
   "Blue2", "Blue3", "Blue4",
   "Red4", "Red3", "Red2"]

rlist = Ngl.Resources()
rlist.wkColorMap = "gsdtol"
#rlist.wkWidth = 700
#rlist.wkHeight = 600
#rlist.wkBackgroundColor = [0.4,0.55,0.35]
rlist.wkBackgroundColor = [1.0,1.0,1.0]
rlist.wkForegroundColor = [0.0,0.0,0.0]

xvsby   = Ngl.open_wks( "ps","vsby",rlist) # Open an X11 workstation.

resources = Ngl.Resources()

resources.sfXCStartV = min(xo)
resources.sfXCEndV   = max(xo)
resources.sfYCStartV = min(yo)
resources.sfYCEndV   = max(yo)

resources.mpProjection = "LambertEqualArea"  # Change the map projection.
resources.mpCenterLonF = -95.
resources.mpCenterLatF = 42.

resources.mpLimitMode = "LatLon"    # Limit the map view.
"""
resources.mpMinLonF   = min(xo)
resources.mpMaxLonF   = max(xo)
resources.mpMinLatF   = min(yo)
resources.mpMaxLatF   = max(yo)
"""
resources.mpMinLonF   = -99.
resources.mpMaxLonF   = -88.
resources.mpMinLatF   = 38.
resources.mpMaxLatF   = 46.
resources.mpPerimOn   = True     

resources.mpOutlineBoundarySets     = "geophysicalandusstates"
resources.mpDataBaseVersion         = "mediumres"            
resources.mpDataSetName             = "Earth..2"
resources.mpGridAndLimbOn = False
resources.mpUSStateLineThicknessF = 2

resources.tiMainString          = "Visibility [%s UTC]"%(mx.DateTime.gmt().strftime("%d %b %Y %H")) 
#resources.tiMainFont            = "Courier"
#resources.tiXAxisString         = "x values"    # X axis label.
#resources.tiYAxisString         = "y values"    # Y axis label.
#resources.tiDeltaF = 1.0 
resources.tiMainFontAspectF = 2.

resources.cnLevelSelectionMode = "ExplicitLevels"
resources.cnLevels  = [0.01,0.1,0.25,0.5,1,2,3,5,8,10]
#resources.cnFillColors = [-1, 91,81,74,68,63,59,45,41,36,30,23,13]
resources.cnFillOn              = True     # Turn on contour fill.
resources.cnInfoLabelOn         = False    # Turn off info label.
resources.cnLineLabelsOn        = False    # Turn off line labels.
 
resources.lbOrientation         = "Horizontal" # Draw it horizontally.
                                                  # label bar.
resources.nglSpreadColors = True    # Do not interpolate color space.
#resources.vpXF = 0.05   # Change Y location of plot.
#resources.vpYF = 0.95   # Change Y location of plot.
#resources.vpHeightF = 0.2
#resources.vpWidthF = 0.2
#resources.vpXF = 0.1
#resources.vpYF = 0.9 

#resources.nglMaximize = True
resources.lbTitleString = "miles"

vsby = numpy.transpose(vsby)
contour = Ngl.contour_map(xvsby,vsby,resources) 
del contour

 
Ngl.end()

os.system("convert -trim  vsby.ps vsby.png")
#os.system("mv test.png /mesonet/share/pickup/test3.png")
si,so = os.popen4("/home/ldm/bin/pqinsert -p \"plot ac %s00 vsby_contour.png vsby_contour_%s00.png png\" vsby.png" % (mx.DateTime.gmt().strftime("%Y%m%d%H"), mx.DateTime.gmt().strftime("%H") ) ) 
