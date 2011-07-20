#!/mesonet/python/bin/python

import sys
sys.path.insert(0, "../../scripts/iemre/")
sys.path.insert(1, "/mesonet/www/apps/iemwebsite/scripts/lib/")
import os
import cgi
import constants
try:
    import netCDF3
except:
    import netCDF4 as netCDF3
import mx.DateTime
import simplejson
import numpy
import shapelib
import dbflib
import shutil
import zipfile

os.chdir("/tmp")

form = cgi.FormContent()
ts0 = mx.DateTime.strptime( form["date0"][0], "%Y-%m-%d")
ts1 = mx.DateTime.strptime( form["date1"][0], "%Y-%m-%d")
base = int(form["base"][0])
ceil = int(form["ceil"][0])
# Make sure we aren't in the future
tsend = mx.DateTime.today()
if ts1 >= tsend:
    ts1 = tsend - mx.DateTime.RelativeDateTime(days=1)
format = form["format"][0]

offset0 = int((ts0 - (ts0 + mx.DateTime.RelativeDateTime(month=1,day=1))).days)
offset1 = int((ts1 - (ts1 + mx.DateTime.RelativeDateTime(month=1,day=1))).days)


fp = "/mnt/mesonet/data/iemre/%s_daily.nc" % (ts0.year,)
nc = netCDF3.Dataset("/mnt/mesonet/data/iemre/%s_daily.nc" % (ts0.year,), 'r')

# 2-D precipitation, inches
precip = numpy.sum(nc.variables['p01d'][offset0:offset1,:,:] / 25.4, axis=0)

# GDD
H = constants.k2f(nc.variables['high_tmpk'][offset0:offset1])
H = numpy.where( H < base, base, H)
H = numpy.where( H > ceil, ceil, H)
L = constants.k2f(nc.variables['low_tmpk'][offset0:offset1])
L = numpy.where( L < base, base, L)
gdd = numpy.sum((H+L)/2.0 - base, axis=0)

nc.close()

if format == 'json':
    # For example: 19013
    ugc = "IAC"+ form["county"][0][2:]
    # Go figure out where this is!
    import iemdb
    postgis = iemdb.connect('postgis', bypass=True)
    pcursor = postgis.cursor()
    pcursor.execute("""
    SELECT x(ST_Centroid(geom)), y(ST_Centroid(geom)) from nws_ugc WHERE
    ugc = %s
    """, (ugc,))
    row = pcursor.fetchone()
    lat = row[1]
    lon = row[0]
    i,j = constants.find_ij(lon, lat)
    myGDD = gdd[j,i]
    myPrecip = precip[j,i]
    res = {'data': [], }
    res['data'].append({
                'gdd': "%.0f" % (myGDD,),
    'precip': "%.1f" % (myPrecip,),
    'latitude': "%.4f" % (lat,),
    'longitude': "%.4f" % (lon,)
       })
    print 'Content-type: text/plain\n'
    print simplejson.dumps( res )

if format == 'shp':
    # Time to create the shapefiles
    fp = "iemre_%s_%s" % (ts0.strftime("%Y%m%d"), ts1.strftime("%Y%m"))
    shp = shapelib.create("%s.shp" % (fp,), shapelib.SHPT_POLYGON)
    
    for x in constants.XAXIS:
      for y in constants.YAXIS:
        obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1,
           [[(x,y),(x,y+constants.DY),(x+constants.DX,y+constants.DY),
             (x+constants.DX,y),(x,y)]])
        shp.write_object(-1, obj)
    
    del(shp)
    dbf = dbflib.create(fp)
    dbf.add_field("GDD", dbflib.FTDouble, 10, 2)
    dbf.add_field("PREC_IN", dbflib.FTDouble, 10, 2)
    
    cnt = 0
    for i in range(len(constants.XAXIS)):
      for j in range(len(constants.YAXIS)):
        dbf.write_record(cnt, {'PREC_IN': precip[j,i], 'GDD': gdd[j,i]})
        cnt += 1
    
    del(dbf)
    
    # Create zip file, send it back to the clients
    shutil.copyfile("/mesonet/data/gis/meta/4326.prj", fp+".prj")
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
    
    

