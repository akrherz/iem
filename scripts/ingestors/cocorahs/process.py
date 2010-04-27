# Process CoCoRaHS Stations!

import sys, urllib2, os, mx.DateTime
from pyIEM import iemdb, iemAccessOb, iemAccessDatabase
i = iemdb.iemdb()
mesosite = i['mesosite']
iemdb = iemAccessDatabase.iemAccessDatabase()

now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(hours=3)

state = sys.argv[1]

url = "http://data.cocorahs.org/Cocorahs/export/exportreports.aspx?ReportType=Daily&dtf=1&Format=CSV&State=%s&ReportDateType=timestamp&Date=%s&TimesInGMT=False" % (state, now.strftime("%m/%d/%Y%%20%H:00%%20%P") ) 
req = urllib2.Request( url )
data = urllib2.urlopen(req).readlines()


# Process Header
header = {}
h = data[0].split(",")
for i in range(len( h )):
  header[ h[i] ] = i

if not header.has_key('StationNumber'):
  sys.exit()

def safeP(v):
  v = v.strip()
  if (v == "T"):
    return 0.0001
  if (v == "NA"):
    return -99
  return v

for row in  data[1:]:
  cols = row.split(",")
  id = cols[ header["StationNumber"] ].strip()

  t = "%s %s" % (cols[ header["ObservationDate"] ], cols[ header["ObservationTime"] ].strip())
  ts = mx.DateTime.strptime(t, "%Y-%m-%d %I:%M %p")
  iem = iemAccessOb.iemAccessOb(id)
  iem.setObTime( ts )
  iem.data['pday'] = safeP(cols[ header["TotalPrecipAmt"] ])
  if (cols[ header["NewSnowDepth"] ].strip() != "NA"):
    iem.data['snow'] = safeP(cols[ header["NewSnowDepth"] ])
  if (cols[ header["TotalSnowDepth"] ].strip() != "NA"):
    iem.data['snowd'] = safeP(cols[ header["TotalSnowDepth"] ])
  iem.updateDatabase(iemdb)
  del iem
