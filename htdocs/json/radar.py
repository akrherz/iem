#!/usr/bin/env python
"""
Return JSON metadata for nexrad information
$Id: $:
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
    'N0Q': 'High res reflectivity'
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
    Return available RADAR sites for the given location
    """
    lat = form.getvalue('lat', 41.99)
    lon = form.getvalue('lon', -95.0)
    MESOSITE = iemdb.connect('mesosite', bypass=True)
    mcursor = MESOSITE.cursor()
    root = {'radars': []}
    mcursor.execute("""
    select id, name, 
    ST_Distance(geom, GeomFromEWKT('SRID=4326;POINT(%s %s)')) as dist 
    from stations where network in ('NEXRAD','ASR4','ASR11','TWDR') 
    and ST_Distance(geom, GeomFromEWKT('SRID=4326;POINT(%s %s)')) < 3 
    ORDER by dist asc
    """ % (lon, lat, lon, lat))
    root['radars'].append({'id': 'USCOMP', 'name': 'National Composite'})
    for row in mcursor:
        root['radars'].append({'id': row[0], 'name': row[1]})
    mcursor.close()
    MESOSITE.close()
    return root

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
    now = start_gts
    if radar in ['USCOMP',]:
        now += mx.DateTime.RelativeDateTime(minutes=(5- now.minute))
        while now < end_gts:
            root['scans'].append({'ts': now.strftime("%Y-%m-%dT%H:%MZ")})
            now += mx.DateTime.RelativeDateTime(minutes=5)
    else:
        while now < end_gts:
            if os.path.isfile( now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/"+
                    radar+"/"+product+"/"+radar+"_"+product+"_%Y%m%d%H%M.png") ):
                root['scans'].append({'ts': now.strftime("%Y-%m-%dT%H:%MZ")})
            now += mx.DateTime.RelativeDateTime(minutes=1)
    
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
        for dir in ['N0Q','N0R']:
            root['products'].append({'id': dir, 'name': NIDS.get(dir,dir)})
    else:
        basedir = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/"+radar)
        if os.path.isdir( basedir ):
            os.chdir( basedir )
            for dir in glob.glob("???"):
                root['products'].append({'id': dir, 'name': NIDS.get(dir,dir)})
    return root
    
def main():
    """
    
    """
    form = cgi.FieldStorage()
    operation = form.getvalue('operation', None)
    if operation == "list":
        print json.dumps( list_files(form) )
    elif operation == "available":
        print json.dumps( available_radars(form) )
    elif operation == "products":
        print json.dumps( list_products(form) )

if __name__ == "__main__":
    print "Content-type: text/plain\n"
    main()