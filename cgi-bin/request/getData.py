#!/mesonet/python/bin/python
# Script to control download of most data from mesonet site
# Daryl Herzmann 19 Nov 2001

import cgi, re, string, sys, mx.DateTime
from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
asosdb = i['asos']
mesositedb = i['mesosite']

def Main():
    print "Content-type: text/plain \n\n",
    form = cgi.FormContent()
    if (not form.has_key("station")):
        print "Station Not defined.  Error"
        sys.exit(0)
    station = (string.strip( form["station"][0] )).upper()
    gisextra = []
    if form.has_key("latlon") and form["latlon"][0] == "yes":
        rs = mesositedb.query("SELECT x(geom) as lon, y(geom) as lat \
             from stations WHERE id = '%s'" % (station,)).dictresult()
        if len(rs) > 0:
            gisextra.append( "%.4f" % (rs[0]['lon'],) )
            gisextra.append( "%.4f" % (rs[0]['lat'],) )
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

    delim = form["format"][0]
    tz = form["tz"][0]
    timeRange = form["timeRange"][0]
    mydb = asosdb

    if timeRange == "allYear":
        sts = sTS + mx.DateTime.RelativeDateTime(month=1,day=1)
        ets = sTS + mx.DateTime.RelativeDateTime(month=1,day=1,years=1)
    elif timeRange == "allMonth":
        sts = sTS + mx.DateTime.RelativeDateTime(day=1)
        ets = sTS + mx.DateTime.RelativeDateTime(months=1,day=1)
    elif timeRange == "rangeDays":
        sts = sTS
        ets = eTS

    if dataVars[0] == "all":
        queryCols = "tmpf, dwpf, relh, drct, sknt, p01m, alti, vsby, gust, skyc1, skyc2, skyc3, skyl1, skyl2, skyl3, metar"
        outCols = ['tmpf','dwpf','relh', 'drct','sknt','p01m','alti','vsby', 'gust',
          'skyc1', 'skyc2', 'skyc3', 'skyl1', 'skyl2', 'skyl3', 'metar']
    else:
        dataVars = tuple(dataVars)
        outCols = dataVars
        dataVars =  str(dataVars)[1:-2]
        queryCols = re.sub("'", " ", dataVars)

    queryStr = """SELECT * from alldata 
      WHERE valid >= '%s' and valid < '%s' and station = '%s' 
      ORDER by valid ASC""" % (sts.strftime("%Y-%m-%d"),
      ets.strftime("%Y-%m-%d"), station)

    if delim == "tab":
        rD = "\t"
        queryCols = re.sub("," , "\t", queryCols) 
    else:
        rD = ","

    if tz == "GMT":
        mydb.query("SET TIME ZONE 'GMT' ")
    #print queryStr
    rs = mydb.query( queryStr ).dictresult()


#    print "#DEBUG: SQL String    -> "+queryStr
    print "#DEBUG: Format Typ    -> "+delim
    print "#DEBUG: Time Zone     -> "+ tz
    print "#DEBUG: Entries Found -> "+ str(len(rs))
    print "station"+rD+"valid ("+tz+" timezone)"+rD,
    if len(gisextra) > 0:
        print "lon"+rD+"lat"+rD,
    print queryCols

    for i in range(len(rs)):
        sys.stdout.write( rs[i]["station"] + rD )
        sys.stdout.write( rs[i]["valid"] + rD )
        sys.stdout.write( rD.join( gisextra ) )
        for data1 in outCols:
            if data1 == 'relh':
               rs[i]['relh'] = mesonet.relh( rs[i]['tmpf'], rs[i]['dwpf'] )
            if data1 in ["metar","skyc1","skyc2","skyc3"]:
                sys.stdout.write("%s%s" % (rs[i][data1], rD))
            elif rs[i][ data1 ] is None or rs[i][ data1 ] <= -99.0:
                sys.stdout.write("M%s" % (rD,))
            else:  
                sys.stdout.write("%2.2f%s" % (rs[i][ data1 ], rD))
        print
Main()
