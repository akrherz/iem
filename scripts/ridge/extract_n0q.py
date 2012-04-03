"""
Extract N0Q values from the raw RIDGE images :)
$Id: $:
"""

import osgeo.gdal as gdal
import mx.DateTime
import glob
import os
from xml.dom.minidom import parse

def parse_colorramp():
    xml = parse("ReflectivityColorCurveManager.xml")
    vals = []
    for level in xml.getElementsByTagName('Level'):
        val = level.getAttribute("upperValue") or level.getAttribute("lowerValue")
        vals.insert(0, float(val) )
    return vals

def get_scans_for_date( ts ):
    """
    Figure out our volume scans for a given date
    """
    dir = ts.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/DMX/N0Q")
    if not os.path.isdir( dir ):
        return
    os.chdir( dir )
    files = glob.glob("*.png")
    files.sort()
    for file in files:
        yield mx.DateTime.strptime(file[8:20], '%Y%m%d%H%M')

def compute_xy(scan, lon, lat):
    """
    Figure out the image navigation
    """
    o = open(scan.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/DMX/N0Q/DMX_N0Q_%Y%m%d%H%M.wld"), 'r')
    lines = o.readlines()
    o.close()
    (dx, blah, blah, dy, x0, y0) = map(float, lines)
    x = int((lon - x0)/dx)
    y = int((lat - y0)/dy)
    return x,y


def get_value(scan, x, y):
    """
    Get the pixel value from a RIDGE file fp
    """
    image = gdal.Open(scan.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/DMX/N0Q/DMX_N0Q_%Y%m%d%H%M.png"), 0)
    array = image.ReadAsArray()
    return array[y,x]
    
def main():
    vals = parse_colorramp()
    lat = 41.53397
    lon = -93.66308
    imgx = None
    imgy = None
    output = open('desmoines.txt', 'a')
    sts = mx.DateTime.DateTime(2001,1,1)
    ets = mx.DateTime.DateTime(2012,4,1)
    interval = mx.DateTime.RelativeDateTime(days=1)
    now = sts
    while now < ets:
        print 'Process', now
        for scan in get_scans_for_date( now ):
            if imgx is None:
                imgx, imgy = compute_xy(scan, lon, lat)
            val = get_value(scan, imgx, imgy)
            output.write("%s,%.2f\n" %(scan, vals[val]))
        now += interval
    output.close()
    
    
main()