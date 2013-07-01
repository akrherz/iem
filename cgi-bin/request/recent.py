#!/usr/bin/env python
"""
Return a simple CSV of recent observations from the database
"""

import psycopg2
import cgi
import sys
import memcache

def run(sid):
    """ run() """
    
    dbconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
    cursor = dbconn.cursor()
    cursor.execute("""SELECT valid at time zone 'UTC', tmpf, dwpf, raw 
     from current_log c JOIN
     stations t on (t.iemid = c.iemid) WHERE t.id = %s
     ORDER by valid ASC""", (sid,))
    
    res = "station,valid,raw\n"
    for row in cursor:
        res += "%s,%s,%s\n" % (sid, row[0].strftime("%Y-%m-%d %H:%M"),
                                         row[3])

    return res

if __name__ == '__main__':
    sys.stdout.write("Content-type: text/plain\n\n")
    form = cgi.FieldStorage()
    sid = form.getfirst('station', 'AMW')[:5]
    
    mckey = "/cgi-bin/request/recent.py|%s" % (sid,)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(sid)
        sys.stdout.write(res)
        mc.set(mckey, res, 300)
    sys.stdout.write( res )
    
