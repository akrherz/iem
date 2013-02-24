#!/usr/bin/env python
"""
Provide nws text in JSON format
"""
import cgi
import datetime
import pytz
import json
import sys
sys.path.insert(1, "/mesonet/www/apps/iemwebsite/scripts/lib/")

import iemdb
AFOS = iemdb.connect('afos', bypass=True)
acursor = AFOS.cursor()

def main():
    form = cgi.FieldStorage()
    pid = form.getvalue('product_id', '201302241937-KSLC-NOUS45-PNSSLC')
    cb = form.getvalue('callback', None)
    utc = datetime.datetime.strptime(pid[:12], '%Y%m%d%H%M')
    utc = utc.replace( tzinfo=pytz.timezone("UTC") )
    pil = pid[-6:]
    root = {'products': []}
    
    acursor.execute("""SELECT data from products where pil = %s and 
    entered = %s""", (pil, utc))
    for row in acursor:
        root['products'].append({
                                 'data': row[0]
                                 })
    
    print 'Content-type: application/javascript\n'
    if cb is None:
        print json.dumps( root )
    else:
        print "%s(%s)" % (cb, json.dumps( root ))
    
main()