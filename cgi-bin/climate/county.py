#!/usr/bin/env python
"""
Generate cloropleths of Iowa County level data
"""
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import os
os.environ[ 'HOME' ] = '/tmp/'
os.environ[ 'USER' ] = 'nobody'
import cgitb
cgitb.enable()
import datetime
from iem import plot 

import iemplot
import iemre

maue = plot.maue(15)
bins = [0,0.1,0.25,0.5,0.75,1,2,3,4,5,6,7,8,9,10,15]

def get_color(val, minvalue, maxvalue):
    if val <= bins[0]:
        return "None"
    for i in range(1,len(bins)+1):
        if val < bins[i]:
            return maue(i-1)
    return maue(14)

# Third Party Stuff
import netCDF4
import numpy
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import rgb2hex
import matplotlib.patheffects as PathEffects
from osgeo import ogr
from shapely.wkb import loads

nc = netCDF4.Dataset('/mesonet/data/iemre/2012_mw_daily.nc', 'r')
lon = nc.variables['lon'][:]
lat = nc.variables['lat'][:]
lon0 = lon[0]
lat0 = lat[0]
dx = lon[1] - lon[0]
dy = lat[1] - lat[0]

def get_xy(mylon, mylat):
    x = int((mylon - lon0) / dx)
    y = int((mylat - lat0) / dy)
    return x,y
    
idx = iemre.day_idx( datetime.datetime(2012,3,1,1,5) )
idx2 = iemre.day_idx( datetime.datetime(2012,4,1,1,5) )
precip = numpy.sum(nc.variables['p01d'][idx:idx2,:,:],0) / 25.4
maxvalue = numpy.max(precip)
m = plot.MapPlot() 

source = ogr.Open("PG:host=iemdb dbname=postgis user=nobody tables=nws_ugc(tgeom)")
data = source.ExecuteSQL("""
  select ugc, ST_Simplify(geom,0.001) as tgeom,
  x(ST_Centroid(geom)) as lon, y(ST_Centroid(geom)) as lat 
  from nws_ugc WHERE polygon_class = 'C' and state = 'IA'
""")
#print 'Content-type: text/plain\n'
patches = []
while True:
    feature = data.GetNextFeature()
    if not feature:
        break
    
    geom = loads(feature.GetGeometryRef().ExportToWkb())
    for polygon in geom:
        if polygon.exterior is None:
            continue
        x,y = get_xy(feature.GetField("lon"), feature.GetField("lat"))
        v = precip[y,x]
        a = numpy.asarray(polygon.exterior)
        x,y = m.map(a[:,0], a[:,1])
        a = zip(x,y)
        c = get_color(v,0,maxvalue)
        p = Polygon(a, fc=c, ec='k', zorder=2, lw=.1)
        patches.append(p)
        
        x,y = m.map(feature.GetField("lon"), feature.GetField("lat"))
        txt = m.ax.text(x, y, "%.2f" % (v,), zorder=3, ha='center', va='center',
                        color='w')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2, 
                                                     foreground="k")])
    
    feature.Destroy()

m.ax.add_collection(PatchCollection(patches,match_original=True) )

m.make_colorbar( bins , maue)

m.postprocess(web=True)    