# Should be cool!

import Ngl
import numpy
import re, os, sys
import math, pdb
import mx.DateTime
from Scientific.IO.NetCDF import *
from pyIEM import stationTable, iemdb
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
i = iemdb.iemdb()
coop = i['coop']
wepp = i['wepp']

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(hours=27)
t0 = ts - mx.DateTime.RelativeDateTime(months=4) + mx.DateTime.RelativeDateTime(day=1)

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
# first, we figure out the interval from the database
if (ts.month < t0.month):  # overlapping year!
  v = " (valid >= '2000-%s' or valid < '2000-%s') " % (t0.strftime("%m-%d"), ts.strftime("%m-%d"))
else:
  v = " (valid >= '2000-%s' and valid <= '2000-%s') " % (t0.strftime("%m-%d"), ts.strftime("%m-%d"))

sql = "SELECT station, sum(precip) as acc from climate51 \
    WHERE %s and station NOT IN ('ia7842','ia4381', 'ia1063') \
    GROUP by station ORDER by acc ASC" % (v,)
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
    station = rs[i]['station'].upper()
    #print station, rs[i]['acc']
    nrain.append(float(rs[i]['acc']))
    lats.append(st.sts[station]['lat'])
    lons.append(st.sts[station]['lon'])

nrain = numpy.array( nrain )
lats = numpy.array( lats )
lons = numpy.array( lons )

numxout = 40
numyout = 40
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


# Compute obs!
lats = None
lons = None
interval = mx.DateTime.RelativeDateTime(days=1)
now = t0
while (now <= ts):
  fp = "/mnt/a2/wepp/data/rainfall/netcdf/daily/%s_rain.nc" % (now.strftime("%Y/%m/%Y%m%d") ,) 
  if not os.path.isfile(fp):
    print fp
  nc = NetCDFFile(fp)
  if (lats is None):
    ncrain = numpy.ravel(nc.variables["rainfall_1day"]) / 25.4
    lats = numpy.ravel(nc.variables["latitude"])
    lons = numpy.ravel(nc.variables["longitude"])
    now += interval
    continue
  a = numpy.ravel(nc.variables["rainfall_1day"]) / 25.4
  # No daily values over 10 inches, sigh
  #a = numpy.where(a>10,0,a)
  b = ncrain
  ncrain = a + b
  #print now, max(a), max(ncrain)
  if (max(a) > 10):
    print "MAX RAIN>10 DATE:%s VALUE:%s" % (now, max(a))
  now += interval

zobs = Ngl.natgrid(lons, lats, ncrain, xo, yo)
# Kill DVN troubles :(
zobs[34,15] = zobs[33,14]
#numpy.putmask(zobs, numpy.where( zobs> 40, 1,0), z)

zavg = nine_smooth2D( zavg )
#zobs = nine_smooth2D( zobs )
#zdiff = (zobs / zavg) * 100.0
zdiff = zobs - zavg

#smax =  int( max( [ math.fabs(max(max(zdiff))), math.fabs(min(min(zdiff))) ] ) + 2.0)
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
#rlist.wkColorMap = "BlWhRe"
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
resources.pmTickMarkDisplayMode = "Never"

resources.mpOutlineBoundarySets     = "AllBoundaries"
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


#resources.cnLevelSelectionMode = 'ManualLevels'
#resources.cnMaxLevelCount  = 15
#resources.cnLevelSpacingF = 1.0
#resources.cnMinLevelValF = 0-smax
#resources.cnMaxLevelValF = smax
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

#resources.tiMainString = "%% of normal %s - %s" % (t0.strftime("%b %d %Y"), ts.strftime("%b %d %Y"), )
resources.tiMainString = "Departure from normal %s - %s" % (t0.strftime("%b %d %Y"), ts.strftime("%b %d %Y"), )
zdiff = numpy.transpose(zdiff)
contour = Ngl.contour_map(xdiff,zdiff,resources) 
del contour

resources.cnLevelSelectionMode = 'AutomaticLevels'
resources.cnLevelSpacingF = 0.5
resources.tiMainString = "Normal Precipitation %s - %s" % (t0.strftime("%b %d"), ts.strftime("%b %d"), )
zavg = numpy.transpose(zavg)
contour = Ngl.contour_map(xavg,zavg,resources) 
del contour

resources.tiMainString          = "Observed Precipitation %s - %s" % (t0.strftime("%b %d %Y"), ts.strftime("%b %d %Y"), )
resources.cnLevelSpacingF = 5.
zobs = numpy.transpose(zobs)
contour = Ngl.contour_map(xobs,zobs,resources) 
del contour
 
Ngl.end()
os.system("convert -trim obs.ps obs.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/4mon_stage4obs.png bogus png' obs.png")
os.remove("obs.ps")
os.remove("obs.png")

os.system("convert -trim  norms.ps norms.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/4mon_normals.png bogus png' norms.png")
os.remove("norms.ps")
os.remove("norms.png")

os.system("convert -trim  diff.ps diff.png")
os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 summary/4mon_diff.png bogus png' diff.png")
os.remove("diff.ps")
os.remove("diff.png")
