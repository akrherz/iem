#!/usr/bin/python
"""
Download interface for ASOS/AWOS data from the asos database
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
    if (not form.has_key("station")):
        print "Station Not defined.  Error"
        sys.exit(0)
    station = (string.strip( form["station"][0] )).upper()
    gisextra = []
    if form.has_key("latlon") and form["latlon"][0] == "yes":
        mcursor.execute("""SELECT x(geom) as lon, y(geom) as lat 
             from stations WHERE id = '%s'""" % (station,))
        if mcursor.rowcount > 0:
            row = mcursor.fetchone()
            gisextra.append( "%.4f" % (row['lon'],) )
            gisextra.append( "%.4f" % (row['lat'],) )
    dataVars = form["data"]
    if form.has_key("year"):
      year1 = int(form["year"][0])
      year2 = int(form["year"][0])
    else:
      year1 = int(form["year1"][0])
      year2 = int(form["year2"][0])
    month1 = int(form["month1"][0])
    month2 = int(form["month2"][0])
    day1 = int(form["day1"][0])
    day2 = int(form["day2"][0])
    try:
        sTS = mx.DateTime.DateTime(year1, month1, day1)
        eTS = mx.DateTime.DateTime(year2, month2, day2)
    except:
        print "MALFORMED DATE:"
        sys.exit()
    if sTS == eTS:
        eTS = sTS + mx.DateTime.RelativeDateTime(days=1)

    delim = form["format"][0]
    tz = form["tz"][0]
    #timeRange = form["timeRange"][0]

    #if timeRange == "allYear":
    #    sts = sTS + mx.DateTime.RelativeDateTime(month=1,day=1)
    #    ets = sTS + mx.DateTime.RelativeDateTime(month=1,day=1,years=1)
    #elif timeRange == "allMonth":
    #    sts = sTS + mx.DateTime.RelativeDateTime(day=1)
    #    ets = sTS + mx.DateTime.RelativeDateTime(months=1,day=1)
    #elif timeRange == "rangeDays":
    sts = sTS
    ets = eTS

    if dataVars[0] == "all":
        queryCols = "tmpf, dwpf, relh, drct, sknt, p01i, alti, vsby, gust, skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, metar"
        outCols = ['tmpf','dwpf','relh', 'drct','sknt','p01i','alti','vsby', 'gust',
          'skyc1', 'skyc2', 'skyc3', 'skyc4', 'skyl1', 'skyl2', 'skyl3', 'skyl4', 'metar']
    else:
        dataVars = tuple(dataVars)
        outCols = dataVars
        dataVars =  str(dataVars)[1:-2]
        queryCols = re.sub("'", " ", dataVars)

    queryStr = """SELECT * from alldata 
      WHERE valid >= '%s' and valid < '%s' and station = '%s' 
      ORDER by valid ASC""" % (sts.strftime("%Y-%m-%d"),
      ets.strftime("%Y-%m-%d"), station)

    if delim == "tdf":
        rD = "\t"
        queryCols = re.sub("," , "\t", queryCols) 
    else:
        rD = ","

    if tz == "GMT":
        acursor.execute("SET TIME ZONE 'GMT' ")
    #print queryStr
    acursor.execute( queryStr )


#    print "#DEBUG: SQL String    -> "+queryStr
    print "#DEBUG: Format Typ    -> "+delim
    print "#DEBUG: Time Zone     -> "+ tz
    print "#DEBUG: Entries Found -> %s" % (acursor.rowcount,)
    print "station"+rD+"valid ("+tz+" timezone)"+rD,
    if len(gisextra) > 0:
        print "lon"+rD+"lat"+rD,
    print queryCols

    gtxt = ""
    if len(gisextra) > 0:
        gtxt = rD.join( gisextra ) + rD

    for row in acursor:
        sys.stdout.write( row["station"] + rD )
        sys.stdout.write( row["valid"].strftime("%Y-%m-%d %H:%M") + rD )
        sys.stdout.write( gtxt )
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
