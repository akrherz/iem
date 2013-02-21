"""
Create an analysis of LSR snowfall reports
"""

import sys
import os
import numpy
import iemplot

import datetime
import random
now = datetime.datetime.now()
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

vals = []
valmask = []
lats = []
lons = []
valid = []

iemplot.MW_NY = 30
iemplot.MW_NX = 40
DX = (iemplot.MW_EAST - iemplot.MW_WEST) / iemplot.MW_NX
DY = (iemplot.MW_NORTH - iemplot.MW_SOUTH) / iemplot.MW_NY

def get_gridx(lon):
    pos = int((lon - iemplot.MW_WEST) / DX)
    if pos < 0:
        return 0
    if pos >= iemplot.MW_NX:
        return iemplot.MW_NX - 1
    return pos

def get_gridy(lat):
    pos = int((lat - iemplot.MW_SOUTH) / DY)
    if pos < 0:
        return 0
    if pos >= iemplot.MW_NY:
        return iemplot.MW_NY - 1
    return pos

validgrid = numpy.zeros( (iemplot.MW_NY, iemplot.MW_NX), dtype='float')
valuegrid = numpy.zeros( (iemplot.MW_NY, iemplot.MW_NX), dtype='float')
usegrid = numpy.zeros( (iemplot.MW_NY, iemplot.MW_NX), dtype='int')
usegrid[:,:] = -1.

lats = []
lons = []
vals = []
valmask = []
pcursor.execute("""SELECT state, 
      magnitude, x(geom) as lon, y(geom) as lat, valid
      from lsrs_%s WHERE type in ('S') and magnitude >= 0 and 
      valid > now() - '12 hours'::interval
      ORDER by valid DESC""" % (now.year,))
i = 0
for row in pcursor:
    lat = row[3]
    lon = row[2]
    val = row[1]
    valid = row[4]

    x = get_gridx(lon)
    y = get_gridy(lat)
    
    lats.append( lat )
    lons.append( lon )
    vals.append( val )
    valmask.append( row[0] in ['IA',] )

    if datetime.datetime.utcfromtimestamp(validgrid[y,x]).year == 1970:
        validgrid[y,x] = float(valid.strftime("%s"))
        valuegrid[y,x] = val
        usegrid[y,x] = i
    i += 1

flons = []
flats = []
fvals = []
fmask = []
for y in range(iemplot.MW_NY):
    for x in range(iemplot.MW_NX):
        idx = usegrid[y,x]
        if idx > -1:
            #print 'Value: x:%s y:%s value:%s' %(x,y, vals[idx])
            flons.append( lons[idx] )
            flats.append( lats[idx] )
            fvals.append( vals[idx] )
            fmask.append( True )
        else:
            # Look around this point
            maxi = numpy.max( usegrid[max(0,y-3):min(y+5,iemplot.MW_NY),
                                      max(0,x-3):min(x+5,iemplot.MW_NX)] )

            if maxi == -1:
                lat =  iemplot.MW_SOUTH + (DY * y)
                lon = iemplot.MW_WEST + (DX * x)
                #print 'Assinging x:%s(%.2f) y:%s(%.2f) as zero' % (x, lon, y, lat)
                flons.append( lon )
                flats.append( lat )
                fvals.append( 0.0 )
                fmask.append( False )



cfg = {
 'wkColorMap': 'WhiteBlueGreenYellowRed',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_valuemask'         : fmask,
 '_title'             : "Local Storm Report Snowfall Total Analysis",
 '_valid'             : "Reports past 12 hours: "+ now.strftime("%d %b %Y %I:%M %p"),
 '_showvalues'        : True,
 '_format'            : '%.1f',
 '_MaskZero'          : True,
 'lbTitleString'      : "[in]",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(flons, flats, fvals, cfg)
pqstr = "plot c 000000000000 lsr_snowfall.png bogus png"
thumbpqstr = "plot c 000000000000 lsr_snowfall_thumb.png bogus png"
iemplot.postprocess(tmpfp,pqstr, thumb=True, thumbpqstr=thumbpqstr)

cfg['_midwest'] = True
cfg['_showvalues'] = False
tmpfp = iemplot.simple_contour(flons, flats, fvals, cfg)
pqstr = "plot c 000000000000 mw_lsr_snowfall.png bogus png"
iemplot.postprocess(tmpfp,pqstr)
