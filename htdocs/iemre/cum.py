#!/usr/bin/env python
import sys
import os
import cgi
from pyiem import iemre, datatypes
import netCDF4
import datetime
import json
import numpy
import shapefile
import shutil
import zipfile
import psycopg2

os.chdir("/tmp")

form = cgi.FormContent()
ts0 = datetime.datetime.strptime(form["date0"][0], "%Y-%m-%d")
ts1 = datetime.datetime.strptime(form["date1"][0], "%Y-%m-%d")
base = int(form["base"][0])
ceil = int(form["ceil"][0])
# Make sure we aren't in the future
tsend = datetime.date.today()
if ts1.date() >= tsend:
    ts1 = tsend - datetime.timedelta(days=1)
    ts1 = datetime.datetime(ts1.year, ts1.month, ts1.day)
fmt = form["format"][0]

offset0 = iemre.daily_offset(ts0)
offset1 = iemre.daily_offset(ts1)


fp = "/mesonet/data/iemre/%s_mw_daily.nc" % (ts0.year,)
nc = netCDF4.Dataset("/mesonet/data/iemre/%s_mw_daily.nc" % (ts0.year,), 'r')

# 2-D precipitation, inches
precip = numpy.sum(nc.variables['p01d'][offset0:offset1, :, :] / 25.4, axis=0)

# GDD
H = datatypes.temperature(nc.variables['high_tmpk'][offset0:offset1],
                          'K').value("F")
H = numpy.where(H < base, base, H)
H = numpy.where(H > ceil, ceil, H)
L = datatypes.temperature(nc.variables['low_tmpk'][offset0:offset1],
                          'K').value("F")
L = numpy.where(L < base, base, L)
gdd = numpy.sum((H+L)/2.0 - base, axis=0)

nc.close()

if fmt == 'json':
    # For example: 19013
    ugc = "IAC" + form["county"][0][2:]
    # Go figure out where this is!
    postgis = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    pcursor = postgis.cursor()
    pcursor.execute("""
    SELECT ST_x(ST_Centroid(geom)), ST_y(ST_Centroid(geom)) from ugcs WHERE
    ugc = %s and end_ts is null
    """, (ugc,))
    row = pcursor.fetchone()
    lat = row[1]
    lon = row[0]
    (i, j) = iemre.find_ij(lon, lat)
    myGDD = gdd[j, i]
    myPrecip = precip[j, i]
    res = {'data': [], }
    res['data'].append({
                'gdd': "%.0f" % (myGDD,),
                'precip': "%.1f" % (myPrecip,),
                'latitude': "%.4f" % (lat,),
                'longitude': "%.4f" % (lon,)
       })
    sys.stdout.write('Content-type: application/json\n\n')
    sys.stdout.write(json.dumps(res))

if fmt == 'shp':
    # Time to create the shapefiles
    basefn = "iemre_%s_%s" % (ts0.strftime("%Y%m%d"), ts1.strftime("%Y%m"))
    w = shapefile.Writer(shapefile.POLYGON)
    w.field('GDD', 'D', 10, 2)
    w.field('PREC_IN', 'D', 10, 2)

    for x in iemre.XAXIS:
        for y in iemre.YAXIS:
            w.poly(parts=[[(x, y), (x, y+iemre.DY),
                           (x+iemre.DX, y+iemre.DY),
                           (x+iemre.DX, y), (x, y)]])

    for i in range(len(iemre.XAXIS)):
        for j in range(len(iemre.YAXIS)):
            w.record(gdd[j, i], precip[j, i])
    w.save(basefn)
    # Create zip file, send it back to the clients
    shutil.copyfile("/opt/iem/data/gis/meta/4326.prj", "%s.prj" % (basefn, ))
    z = zipfile.ZipFile("%s.zip" % (basefn,), 'w', zipfile.ZIP_DEFLATED)
    for suffix in ['shp', 'shx', 'dbf', 'prj']:
        z.write("%s.%s" % (basefn, suffix))
    z.close()

    sys.stdout.write("Content-type: application/octet-stream\n")
    sys.stdout.write(("Content-Disposition: attachment; filename=%s.zip\n\n"
                      ) % (basefn, ))

    sys.stdout.write(file(basefn+".zip", 'r').read())

    for suffix in ['zip', 'shp', 'shx', 'dbf', 'prj']:
        os.unlink("%s.%s" % (basefn, suffix))
