#!/mesonet/python/bin/python
# Script to control download of most data from mesonet site
# Daryl Herzmann 19 Nov 2001

import cgi, re, string, sys, mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
asosdb = i['asos']
rwisdb = i['rwis']
mesositedb = i['mesosite']

def Main():
    print 'Content-type: text/plain \n\n'
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
    year = int(form["year"][0])
    month1 = int(form["month1"][0])
    month2 = int(form["month2"][0])
    day1 = int(form["day1"][0])
    day2 = int(form["day2"][0])
    try:
        sTS = mx.DateTime.DateTime(year, month1, day1)
        eTS = mx.DateTime.DateTime(year, month2, day2)
    except:
        print "MALFORMED DATE:"
        sys.exit()

    delim = form["format"][0]
    tz = form["tz"][0]
    tableName = "t%s" % ( sTS.year, )
    timeRange = form["timeRange"][0]
    include20s = form["include20s"][0]
    mydb = asosdb
    if len(station) > 3:
        mydb = rwisdb

    timeConstraint = ""
    if (include20s == "no"):
        timeConstraint = " and date_part('minute', valid) = 0 "

    if (timeRange == "allYear"):
        timeStr = "date_part('year', valid) = %s" % ( sTS.year, )
    elif (timeRange == "allMonth"):
        timeStr = "date_part('month', valid) = %s" % (sTS.month, )
    elif (timeRange == "rangeMonth"):
        timeStr = "date(valid) >= '%s' and date(valid) <= '%s'" % (sTS.strftime("%Y-%m-01"), (eTS + mx.DateTime.RelativeDateTime(months=+1, days=-1)).strftime("%Y-%m-%d") ) 
    elif (timeRange == "allDay"):
        timeStr = "date(valid) = '%s'" % (sTS.strftime("%Y-%m-%d"),)
    elif (timeRange == "rangeDays"):
        timeStr = "date(valid) >= '%s' and date(valid) <= '%s' " % (sTS.strftime("%Y-%m-%d"), eTS.strftime("%Y-%m-%d") )

    if (dataVars[0] == "all" and len(station) == 3):
        queryCols = "tmpf, dwpf, drct, sknt, skyc, p01m,alti,vsby"
        outCols = ['tmpf','dwpf','drct','sknt','skyc','p01m','alti','vsby']
    elif (dataVars[0] == "all"):
        queryCols = "tmpf, dwpf, drct, sknt"
        outCols = ['tmpf','dwpf','drct','sknt']

    else:
        dataVars = tuple(dataVars)
        outCols = dataVars
        dataVars =  str(dataVars)[1:-2]
        queryCols = re.sub("'", " ", dataVars)

    queryStr = "SELECT station, valid, "+ queryCols +" from "+ tableName +" WHERE "+ timeStr +" and station = '"+ station +"' "+ timeConstraint +" ORDER by valid"

    if delim == "space":
        rD = " "
        queryCols = re.sub("," , " ", queryCols)
    elif delim == "tab":
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
        print rs[i]["station"] + rD ,
        print rs[i]["valid"] + rD , 
        print rD.join( gisextra ),
        for data1 in outCols:
            if rs[i][ data1 ] is None or rs[i][ data1 ] <= -99.0:
                print "M%s" % (rD,),
            else:  
                print "%2.2f%s" % (rs[i][ data1 ], rD),
        print
Main()
