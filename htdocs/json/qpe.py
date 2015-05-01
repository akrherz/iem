#!/usr/bin/env python
"""
JSON backend for precip data, we get URL rewritten to get here....
"""
import cgi
import json
import mx.DateTime
import gdal
import os
import sys


def get_5():
    gmt = mx.DateTime.gmt()
    gmt -= mx.DateTime.RelativeDateTime(minutes=gmt.minute % 5)
    return gmt


def sample(fp, lon, lat):
    """
    Sample a file
    """
    # Wold file
    o = open(fp[:-4]+".wld", 'r')
    lines = o.readlines()
    o.close()
    (dx, _, _, dy, x0, y0) = map(float, lines)
    x = int((lon - x0)/dx)
    y = int((lat - y0)/dy)
    image = gdal.Open(fp)
    ar = image.ReadAsArray()
    return ar[y, x]


def five_minute(lon, lat):
    """
    Five minute Intensity
    """
    gmt = get_5()
    attempt = 0
    realfp = None
    while attempt < 10:
        fp = gmt.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/"
                           "GIS/q2/r5m_%Y%m%d%H%M.png"))
        if os.path.isfile(fp):
            realfp = fp
            break
        gmt -= mx.DateTime.RelativeDateTime(minutes=5)
        attempt += 1
    if not realfp:
        return {}
    return {
            'value': sample(realfp, gmt, lon, lat),
            'start_time': (gmt - mx.DateTime.RelativeDateTime(
                                                    minutes=5)).strftime("")
            }


if __name__ == '__main__':
    """
    Main
    """
    form = cgi.FieldStorage()
    lat = float(form.getvalue('lat'))
    lon = float(form.getvalue('lon'))
    sys.stdout.write('Content-type: application/json\n\n')
    sys.stdout.write(json.dumps({"ERROR": "No data found"}))
    # sys.stdout.write(json.dump( five_minute(lon, lat) ))
