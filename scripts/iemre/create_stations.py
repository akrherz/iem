'''
 We are going to create stations based on our IEMRE grid
'''
import netCDF4
import numpy as np
import psycopg2
import json
import urllib2

PGCONN = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = PGCONN.cursor()

PGCONN = psycopg2.connect(database='mesosite')
mcursor = PGCONN.cursor()

def get_name(lon, lat):
    mindist = 999
    name = None
    for line in open('/home/akrherz/Downloads/cities1000.txt'):
        tokens = line.split("\t")
        slat = float(tokens[4])
        slon = float(tokens[5])
        dist = ((slat - lat)**2 + (slon - lon)**2)**.5
        if dist < mindist:
            name = tokens[1]
            mindist = dist
    return name

nc = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")

lats = nc.variables['lat'][:]
lons = nc.variables['lon'][:]

domain = nc.variables['domain'][:]

delta = 0.125

seq = 0
for j in range(len(lats)):
    for i in range(len(lons)):
        if domain[j,i] > 0:
            lat = lats[j] + delta
            lon = lons[i] + delta
            wkt = "ST_GeomFromEWKT('SRID=4326;POINT(%s %s)')" % (lon, lat)
            
            cursor.execute("""
            SELECT state_abbr from states where ST_Contains(the_geom, %s)
            """ % (wkt,))
            if cursor.rowcount != 1:
                continue
            st = cursor.fetchone()[0]
            stid = "%s%04i" % (st, seq)
            network = "%s_IEMRE" % (st,)
            name = get_name(lon, lat)
            mcursor.execute("""INSERT into stations
            (id, name, state, network, online, geom, metasite) VALUES
            (%s,%s,%s,%s,'t','SRID=4326;POINT(%s %s)', 't')""", 
            (stid, name, st, network, lon, lat))
            
            seq += 1
            
mcursor.close()
PGCONN.commit()
PGCONN.close()
            