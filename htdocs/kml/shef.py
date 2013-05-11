#!/usr/bin/env python
"""
 /kml/shef_4inch.kml
"""

import simplekml
import cgi
import psycopg2
import memcache
import sys

def run():
    """ run! """
    
    kml = simplekml.Kml()
    pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = pgconn.cursor()
    cursor.execute(""" 
        select distinct station, valid, value, ST_x(t.geom), ST_y(t.geom) 
        from current_shef c JOIN stations t on (t.id = c.station) where 
        depth = 4 and valid > '2013-05-10' and extremum = 'Z' and value > -90
    """)
    for row in cursor:
        pt = kml.newpoint()
        pt.name = '%.0f' % (row[2],)
        pt.description = '%s %.0f' % (row[0], row[2])
        pt.coords = [(row[3], row[4])]
    
    return kml.kml(False)
    
if __name__ == '__main__':
    """ main """
    # Figure out what is wanted
    form = cgi.FieldStorage()
    mode = form.getfirst('mode', '4inch')
    if mode == '4inch':
        depth = 4
        fn = 'shef_4inch.kml'
    

    mc = memcache.Client(['iem-memcached:11211'])
    cache = mc.get(fn)
    sys.stdout.write("Content-type: application/vnd.google-earth.kml+xml\n\n")
    if cache:
        sys.stderr.write("Using memcache for: %s" % (fn,))
        sys.stdout.write( cache )
    else:
        data = run()
        mc.set(fn, data, time=1800)
        sys.stdout.write( data )