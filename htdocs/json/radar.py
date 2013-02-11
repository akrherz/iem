#!/usr/bin/env python
"""
Return JSON metadata for nexrad information
"""
import sys
sys.path.insert(1, "/mesonet/www/apps/iemwebsite/scripts/lib/")
import cgi
import json
import mx.DateTime
import os
import iemdb
import glob

NIDS = {
    'N0Q': 'Base Reflectivity (High Res)',
    'N0U': 'Base Radial Velocity (High Res)',
    'N0S': 'Storm Relative Radial Velocity',
    'NET': 'Echo Tops',
    'N0R': 'Base Reflectivity',
    'N0V': 'Base Radial Velocity',
    'N0Z': 'Base Reflectivity',
    'TR0': 'TDWR Base Reflectivity',
    'TV0': 'TDWR Radial Velocity',
}

def parse_time(s):
    """
    Convert ISO something into a mx.DateTime
    """
    try:
        date = mx.DateTime.strptime(s, '%Y-%m-%dT%H:%MZ')
    except:
        date = mx.DateTime.gmt()
    return date

def available_radars(form):
    """
    Return available RADAR sites for the given location and date!
    """
    lat = form.getvalue('lat', None)
    lon = form.getvalue('lon', None)
    start_gts = parse_time( form.getvalue('start', '2012-01-27T00:00Z') )
    MESOSITE = iemdb.connect('mesosite', bypass=True)
    mcursor = MESOSITE.cursor()
    root = {'radars': []}
    if lat is None or lon is None:
        sql = """
        select id, name,
        x(geom) as lon, y(geom) as lat, network
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR') 
        ORDER by id asc"""
    else:
        sql = """
        select id, name, x(geom) as lon, y(geom) as lat, network, 
        ST_Distance(geom, GeomFromEWKT('SRID=4326;POINT(%s %s)')) as dist 
        from stations where network in ('NEXRAD','ASR4','ASR11','TWDR') 
        and ST_Distance(geom, GeomFromEWKT('SRID=4326;POINT(%s %s)')) < 3 
        ORDER by dist asc
        """ % (lon, lat, lon, lat)
    mcursor.execute(sql)
    root['radars'].append({'id': 'USCOMP', 'name': 'National Composite',
                           'lat': 42.5, 'lon': -95, 'type': 'COMPOSITE'})
    for row in mcursor:
        radar = row[0]
        if not os.path.isdir(start_gts.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/"+
                    radar)):
            continue
        root['radars'].append({'id': radar, 'name': row[1], 'lat': row[3], 
                               'lon': row[2], 'type': row[4]})
    mcursor.close()
    MESOSITE.close()
    return root

def find_scans(root, radar, product, sts, ets):
    """
    Find scans for a given radar, product, and start and end time
    """
    now = sts
    if radar in ['USCOMP',]:
        now -= mx.DateTime.RelativeDateTime(minutes=(now.minute % 5))
        while now < ets and len(root['scans']) < 501:
            if os.path.isfile( now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/"+
                    product.lower() +"_%Y%m%d%H%M.png") ):
                root['scans'].append({'ts': now.strftime("%Y-%m-%dT%H:%MZ")})
            now += mx.DateTime.RelativeDateTime(minutes=5)
    else:
        while now < ets and len(root['scans']) < 501:
            if os.path.isfile( now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/"+
                    radar+"/"+product+"/"+radar+"_"+product+"_%Y%m%d%H%M.png") ):
                root['scans'].append({'ts': now.strftime("%Y-%m-%dT%H:%MZ")})
            now += mx.DateTime.RelativeDateTime(minutes=1)

def is_realtime(sts):
    """
    Check to see if this time is close to realtime...
    """
    if (mx.DateTime.gmt() - sts).seconds > 3600:
        return False
    return True

def list_files(form):
    """
    List available NEXRAD files based on the form request
    """
    radar = form.getvalue('radar', 'DMX')[:10]
    product = form.getvalue('product', 'N0Q')[:3]
    start_gts = parse_time( form.getvalue('start', '2012-01-27T00:00Z') )
    end_gts = parse_time( form.getvalue('end', '2012-01-27T01:00Z') )
    #root = {'metaData': {'nexrad': nexrad, 'product': product}, 'scans' : []}
    root = {'scans': []}
    find_scans(root, radar, product, start_gts, end_gts)
    if len(root['scans']) == 0 and is_realtime(start_gts):
        now = start_gts - mx.DateTime.RelativeDateTime(minutes=10)
        find_scans(root, radar, product, now, end_gts)
        
    return root

def list_products(form):
    """
    List available NEXRAD products
    """
    radar = form.getvalue('radar', 'DMX')[:10]
    now = parse_time( form.getvalue('start', '2012-01-27T00:00Z') )
    #root = {'metaData': {'nexrad': nexrad, 'product': product}, 'scans' : []}
    root = {'products': []}
    if radar == 'USCOMP':
        for dirname in ['N0Q','N0R']:
            testfp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/"+
                                  dirname.lower()+"_%Y%m%d0000.png")
            if os.path.isfile(testfp):
                root['products'].append({'id': dirname, 
                                         'name': NIDS.get(dir,dir)})
    else:
        basedir = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/"+radar)
        if os.path.isdir( basedir ):
            os.chdir( basedir )
            for dirname in glob.glob("???"):
                root['products'].append({'id': dirname, 
                                         'name': NIDS.get(dir,dir)})
    return root
    
def main():
    """
    
    """
    form = cgi.FieldStorage()
    operation = form.getvalue('operation', None)
    callback = form.getvalue('callback', None)
    if callback is not None:
        print "Content-type: application/javascript\n"
        print "%s(" % (callback,),
    else:
        print "Content-type: text/plain\n"
    if operation == "list":
        print json.dumps( list_files(form) ),
    elif operation == "available":
        print json.dumps( available_radars(form) ),
    elif operation == "products":
        print json.dumps( list_products(form) ),
    if callback is not None:
        print ')',

if __name__ == "__main__":
    main()
#END