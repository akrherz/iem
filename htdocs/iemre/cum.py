#!/usr/bin/env python
import sys
import os
import cgi
from pyiem import iemre, datatypes
import netCDF4
import datetime
import json
import numpy
import shapelib
import dbflib
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

if format == 'shp':
    # Time to create the shapefiles
    fp = "iemre_%s_%s" % (ts0.strftime("%Y%m%d"), ts1.strftime("%Y%m"))
    shp = shapelib.create("%s.shp" % (fp,), shapelib.SHPT_POLYGON)

    for x in iemre.XAXIS:
        for y in iemre.YAXIS:
            obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1,
                                     [[(x, y), (x, y+iemre.DY),
                                       (x+iemre.DX, y+iemre.DY),
                                       (x+iemre.DX, y), (x, y)]])
            shp.write_object(-1, obj)

    del(shp)
    dbf = dbflib.create(fp)
    dbf.add_field("GDD", dbflib.FTDouble, 10, 2)
    dbf.add_field("PREC_IN", dbflib.FTDouble, 10, 2)

    cnt = 0
    for i in range(len(iemre.XAXIS)):
        for j in range(len(iemre.YAXIS)):
            dbf.write_record(cnt, {'PREC_IN': precip[j, i],
                                   'GDD': gdd[j, i]})
            cnt += 1

    del(dbf)

    # Create zip file, send it back to the clients
    shutil.copyfile("/mesonet/www/apps/iemwebsite/data/gis/meta/4326.prj",
                    fp+".prj")
    z = zipfile.ZipFile(fp+".zip", 'w', zipfile.ZIP_DEFLATED)
    z.write(fp+".shp")
    z.write(fp+".shx")
    z.write(fp+".dbf")
    z.write(fp+".prj")
    z.close()

    print "Content-type: application/octet-stream"
    print "Content-Disposition: attachment; filename=%s.zip" % (fp,)
    print

    print file(fp+".zip", 'r').read(),

    os.remove(fp+".zip")
    os.remove(fp+".shp")
    os.remove(fp+".shx")
    os.remove(fp+".dbf")
    os.remove(fp+".prj")
