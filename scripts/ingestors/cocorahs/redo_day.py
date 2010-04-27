# Process CoCoRaHS Stations!

import urllib2, os, mx.DateTime, sys
from pyIEM import iemdb, iemAccessOb, iemAccessDatabase
i = iemdb.iemdb()
mesosite = i['mesosite']
access = i['iem']
iemdb = iemAccessDatabase.iemAccessDatabase()

state = sys.argv[1]

def safeP(v):
  v = v.strip()
  if (v == "T"):
    return 0.0001
  if (v == "NA"):
    return -99
  return float(v)

def runner(days):
  now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=days)

  req = urllib2.Request("http://data.cocorahs.org/Cocorahs/export/exportreports.aspx?ReportType=Daily&dtf=1&Format=CSV&State=%s&ReportDateType=Daily&Date=%s&TimesInGMT=False" % (state, now.strftime("%m/%d/%Y%%20%H:00%%20%P"),) )
  data = urllib2.urlopen(req).readlines()

  # Process Header
  header = {}
  h = data[0].split(",")
  for i in range(len( h )):
    header[ h[i] ] = i


  for row in  data[1:]:
    cols = row.split(",")
    id = cols[ header["StationNumber"] ].strip()

    t = "%s %s" % (cols[ header["ObservationDate"] ], cols[ header["ObservationTime"] ].strip())
    ts = mx.DateTime.strptime(t, "%Y-%m-%d %I:%M %p")

    val = safeP(cols[ header["TotalPrecipAmt"] ])
    #print id, ts, val

    sql = "SELECT pday from summary_%s WHERE station = '%s' and day = '%s'" % (ts.year, id, ts.strftime("%Y-%m-%d") )
    rs = access.query(sql).dictresult()
    if (len(rs) == 0):
      print "ADDING Summary entry for id: %s" % (id,)
      sql = "INSERT into summary_%s(station, geom, network, day, pday)\
      VALUES ('%s', (select geom from current WHERE station = '%s'), '%s', '%s', %s) " \
      % (ts.year, id, id, state+'COCORAHS', ts.strftime("%Y-%m-%d"), val )
      access.query(sql)
    else:
      dbval = float(rs[0]['pday'])
      if (dbval != val):
        print "DB UPDATE [%s] OLD: %s NEW: %s" % (id, dbval, val)
        sql = "UPDATE summary_%s SET pday = %s WHERE station = '%s' and day = '%s'" % (ts.year, val, id, ts.strftime("%Y-%m-%d") )
        access.query(sql)

    #------------------
    val = safeP(cols[ header["NewSnowDepth"] ])

    sql = "SELECT snow from summary_%s WHERE station = '%s' and day = '%s'" % (ts.year, id, ts.strftime("%Y-%m-%d") )
    rs = access.query(sql).dictresult()
    dbval = float(rs[0]['snow'])
    if (dbval != val):
      print "DB SNOW UPDATE [%s] OLD: %s NEW: %s" % (id, dbval, val)
      sql = "UPDATE summary_%s SET snow = %s WHERE station = '%s' and day = '%s'" % (ts.year, val, id, ts.strftime("%Y-%m-%d") )
      access.query(sql)


for i in range(1,15):
  runner(i)
