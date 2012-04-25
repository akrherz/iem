#!/usr/bin/python
"""
Download interface for ASOS/AWOS data from the asos database
$Id: $:
"""

import cgi, re, string, sys
import mx.DateTime
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import iemdb
import mesonet
import psycopg2.extras
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor(cursor_factory=psycopg2.extras.DictCursor)

def main():
    print "Content-type: text/plain \n\n",
    form = cgi.FormContent()
    metadata = {}
    mcursor.execute("""SELECT id, x(geom) as lon, y(geom) as lat 
         from stations WHERE network ~* 'ASOS' or network = 'AWOS'
         and country = 'US' """)
    for row in mcursor:
        metadata[row[0]] = {'lon': "%.4f" % (row[1],), 'lat': "%.4f" % (row[2],)}

    year = int(form["year"][0])
    month = int(form["month"][0])
    day = int(form["day"][0])
    hour = int(form["hour"][0])
    ts = mx.DateTime.DateTime(year, month, day, hour)

    queryCols = "tmpf, dwpf, relh, drct, sknt, p01i, alti, mslp, vsby, gust, skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, metar"
    outCols = ['tmpf','dwpf','relh', 'drct','sknt','p01i','alti','mslp', 'vsby', 'gust',
          'skyc1', 'skyc2', 'skyc3', 'skyc4', 'skyl1', 'skyl2', 'skyl3', 'skyl4', 'metar']
    
    queryStr = """SELECT * from t%s 
      WHERE valid >= '%s' and valid < '%s'  
      ORDER by station ASC""" % (ts.year, 
            (ts - mx.DateTime.RelativeDateTime(minutes=10)).strftime("%Y-%m-%d %H:%M"),
            (ts + mx.DateTime.RelativeDateTime(minutes=1)).strftime("%Y-%m-%d %H:%M"))

    rD = ","

    acursor.execute("SET TIME ZONE 'GMT' ")
    #print queryStr
    acursor.execute( queryStr )

    print "station"+rD+"valid (UTC timezone)"+rD+"lon"+rD+"lat"+rD,
    print queryCols

    for row in acursor:
        if not metadata.has_key(row['station']):
            continue
        sys.stdout.write( row["station"] + rD )
        sys.stdout.write( row["valid"].strftime("%Y-%m-%d %H:%M") + rD )
        sys.stdout.write( metadata[row['station']]['lon'] + rD )
        sys.stdout.write( metadata[row['station']]['lat'] + rD )
        for data1 in outCols:
            if data1 == 'relh':
                val = mesonet.relh( row['tmpf'], row['dwpf'] )
                if val != "M":
                    sys.stdout.write("%.2f%s" % (val, rD))
                else:
                    sys.stdout.write("M%s" % (rD,))
            elif data1 == 'p01m':
                if row['p01i'] >= 0:
                    sys.stdout.write("%.2f%s" % (row['p01i'] * 25.4, rD))
                else:
                    sys.stdout.write("M%s" % (rD,))
            elif data1 == 'tmpc':
                if row['tmpf'] is not None:
                    val = mesonet.f2c( row['tmpf'] )
                    sys.stdout.write("%.2f%s" % (val, rD))
                else:
                    sys.stdout.write("M%s" % (rD,))
            elif data1 == 'dwpc':
                if row['dwpf'] is not None:
                    val = mesonet.f2c( row['dwpf'] )
                    sys.stdout.write("%.2f%s" % (val, rD))
                else:
                    sys.stdout.write("M%s" % (rD,))
            elif data1 in ["metar","skyc1","skyc2","skyc3","skyc4"]:
                sys.stdout.write("%s%s" % (row[data1], rD))
            elif row[ data1 ] is None or row[ data1 ] <= -99.0 or row[ data1 ] == "M":
                sys.stdout.write("M%s" % (rD,))
            else:  
                sys.stdout.write("%2.2f%s" % (row[ data1 ], rD))
        print
        
if __name__ == '__main__':
    main()
