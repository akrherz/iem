# Should be cool!

import Ngl
import numpy
import re, os
import math
import mx.DateTime
from Scientific.IO.NetCDF import *
from pyIEM import stationTable, iemdb
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
i = iemdb.iemdb()
coop = i['coop']

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

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

nrain = []
lats = []
lons = []

# Get normals!
rs = coop.query("SELECT station, sum(precip) as acc from climate51 \
    WHERE valid <= '2000-%s' and station NOT IN ('ia7842','ia4381') \
    GROUP by station ORDER by acc ASC" % (ts.strftime("%m-%d"),) ).dictresult()
for i in range(len(rs)):
    station = rs[i]['station'].upper()
    #print station, rs[i]['acc']
    nrain.append(float(rs[i]['acc']))
    lats.append(st.sts[station]['lat'])
    lons.append(st.sts[station]['lon'])

nrain = numpy.array( nrain )
lats = numpy.array( lats )
lons = numpy.array( lons )

numxout = 20
numyout = 20
xmin    = min(lons) - 0.5
ymin    = min(lats) - 0.5
xmax    = max(lons) + 0.5
ymax    = max(lats) + 0.5

xc      = (xmax-xmin)/(numxout-1)
yc      = (ymax-ymin)/(numyout-1)

xo = xmin + xc*numpy.arange(0,numxout)
yo = ymin + yc*numpy.arange(0,numyout)
zavg = Ngl.natgrid(lons, lats, nrain, xo, yo)
#zavg = nine_smooth2D(zavg)


# Open Obs 
nc = NetCDFFile("/mnt/a2/wepp/data/rainfall/netcdf/yearly/%srain.nc" % (ts.year,) )
ncrain = numpy.ravel(nc.variables["yrrain"])
lats = numpy.ravel(nc.variables["latitude"])
lons = numpy.ravel(nc.variables["longitude"])

zobs = Ngl.natgrid(lons, lats, ncrain, xo, yo)

zavg = nine_smooth2D( zavg )
zobs = nine_smooth2D( zobs )
zdiff = zobs - zavg

smax =  int( max( [ math.fabs(numpy.max(zdiff)), math.fabs(numpy.max(zdiff)) ] ) + 2.0)
#print math.fabs(max(max(zdiff)))
#print math.fabs(min(min(zdiff)))

cmap = numpy.array([[1.00, 1.00, 1.00], [0.00, 0.00, 0.00], \
                       [1.00, 0.00, 0.00], [1.00, 0.00, 0.40], \
                       [1.00, 0.00, 0.80], [1.00, 0.20, 1.00], \
                       [1.00, 0.60, 1.00], [0.60, 0.80, 1.00], \
                       [0.20, 0.80, 1.00], [0.20, 0.80, 0.60], \
                       [0.20, 0.80, 0.00], [0.20, 0.40, 0.00], \
                       [0.20, 0.45, 0.40], [0.20, 0.40, 0.80], \
                       [0.60, 0.40, 0.80], [0.60, 0.80, 0.80], \
                       [0.60, 0.80, 0.40], [1.00, 0.60, 0.80]],numpy.float32)


rlist = Ngl.Resources()
rlist.wkColorMap = "BlWhRe"
#rlist.wkWidth = 700
#rlist.wkHeight = 600
rlist.wkBackgroundColor = [1.0,1.0,1.0]

xdiff   = Ngl.open_wks( "ps","diff",rlist) # Open an X11 workstation.
xavg  = Ngl.open_wks( "ps","norms",rlist) # Open an X11 workstation.
xobs  = Ngl.open_wks( "ps","obs",rlist) # Open an X11 workstation.

resources = Ngl.Resources()

resources.sfXCStartV = min(xo)
resources.sfXCEndV   = max(xo)
resources.sfYCStartV = min(yo)
resources.sfYCEndV   = max(yo)

resources.mpProjection = "LambertEqualArea"  # Change the map projection.
resources.mpCenterLonF = -95.
resources.mpCenterLatF = 42.
#resources.pmTickMarkDisplayMode = "Never"      # Turn off annoying ticks
resources.mpLimitMode = "LatLon"    # Limit the map view.
resources.mpMinLonF   = min(xo)
resources.mpMaxLonF   = max(xo)
resources.mpMinLatF   = min(yo)
resources.mpMaxLatF   = max(yo)
#resources.mpMinLonF   = -96.
#resources.mpMaxLonF   = -90.
#resources.mpMinLatF   = 40.
#resources.mpMaxLatF   = 46.
resources.mpPerimOn   = True     

resources.mpOutlineBoundarySets     = "geophysicalandusstates"
resources.mpDataBaseVersion         = "mediumres"            
resources.mpDataSetName             = "Earth..2"
resources.mpGridAndLimbOn = False
resources.mpUSStateLineThicknessF = 2

resources.tiMainString          = "Growing Degree Day Departure"
#resources.tiMainFont            = "Courier"
#resources.tiXAxisString         = "x values"    # X axis label.
#resources.tiYAxisString         = "y values"    # Y axis label.
#resources.tiDeltaF = 1.0 
resources.tiMainFontAspectF = 2.


resources.cnLevelSelectionMode = 'ManualLevels'
#resources.cnMaxLevelCount  = 15
resources.cnLevelSpacingF = 1.0
resources.cnMinLevelValF = 0-smax
resources.cnMaxLevelValF = smax
resources.cnFillOn              = True     # Turn on contour fill.
resources.cnInfoLabelOn         = False    # Turn off info label.
resources.cnLineLabelsOn        = False    # Turn off line labels.
 
resources.lbOrientation         = "Horizontal" # Draw it horizontally.
                                                  # label bar.
resources.nglSpreadColors = True    # Do not interpolate color space.
resources.nglSpreadColorStart = -1
resources.nglSpreadColorEnd   =  2  

#resources.vpXF = 0.05   # Change Y location of plot.
#resources.vpYF = 0.95   # Change Y location of plot.
#resources.vpHeightF = 0.2
#resources.vpWidthF = 0.2
#resources.vpXF = 0.1
#resources.vpYF = 0.9 

#resources.nglMaximize = True

resources.tiMainString = "Precipitation Departure [inch] Jan 1 - %s" % (ts.strftime("%b %d %Y"), )
resources.pmTickMarkDisplayMode = "Never"
resources.cnLevelSpacingF = 3.0
zdiff = numpy.transpose(zdiff)
contour = Ngl.contour_map(xdiff,zdiff,resources) 
del contour

resources.cnLevelSelectionMode = 'AutomaticLevels'
resources.cnLevelSpacingF = 0.5
resources.tiMainString = "Normal Precipitation Jan 1 - %s" % (ts.strftime("%b %d"), )
zavg = numpy.transpose(zavg)
contour = Ngl.contour_map(xavg,zavg,resources) 
del contour

resources.tiMainString          = "Observed Precipitation Jan 1 - %s" % (ts.strftime("%b %d %Y"), )
resources.cnLevelSpacingF = 2.
zobs = numpy.transpose(zobs)
contour = Ngl.contour_map(xobs,zobs,resources) 
del contour
 
Ngl.end()
os.system("convert -trim obs.ps obs.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/year/stage4obs.png bogus png' obs.png")

os.system("convert -trim  norms.ps norms.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/year/normals.png bogus png' norms.png")

os.system("convert -trim  diff.ps diff.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/year/diff.png bogus png' diff.png")

