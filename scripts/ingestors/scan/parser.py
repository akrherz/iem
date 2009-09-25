
import sys, re, mx.DateTime, pg, urllib2
from pyIEM import iemAccess, iemAccessOb, mesonet, iemAccessDatabase
iemdb = pg.connect("iem", "iemdb")
import string
mydb = pg.connect("scan", "iemdb")


mapping = {
 'BPC': {'iemvar': 'pres', 'multiplier': 1.0 },
 'BPHGC': {'iemvar': 'pres', 'multiplier': 1.0 },
 'RHC':  {'iemvar': 'relh', 'multiplier': 1.0 },
 'RH1C1': {'iemvar': 'relh', 'multiplier': 1.0 },
 'SOLAR': {'iemvar': 'srad', 'multiplier': 1.0 },
 'SRHA': {'iemvar': 'srad', 'multiplier': 1.0 },
 'WNDDA': {'iemvar': 'drct', 'multiplier': 1.0 },
 'WDHA': {'iemvar': 'drct', 'multiplier': 1.0 },
 'WNDSA': {'iemvar': 'sknt', 'multiplier': 0.8689 },
 'WSPHA': {'iemvar': 'sknt', 'multiplier': 0.8689 },
 'ATEC' : {'iemvar': 'tmpc', 'multiplier': 1.0 },
 'ATHC6': {'iemvar': 'tmpc', 'multiplier': 1.0 },
 'C1SMV': {'iemvar': 'c1smv', 'multiplier': 1.0},
 'C2SMV': {'iemvar': 'c2smv', 'multiplier': 1.0},
 'C3SMV': {'iemvar': 'c3smv', 'multiplier': 1.0},
 'C4SMV': {'iemvar': 'c4smv', 'multiplier': 1.0},
 'C5SMV': {'iemvar': 'c5smv', 'multiplier': 1.0},
 'C1TMP': {'iemvar': 'c1tmpc', 'multiplier': 1.0},
 'C2TMP': {'iemvar': 'c2tmpc', 'multiplier': 1.0},
 'C3TMP': {'iemvar': 'c3tmpc', 'multiplier': 1.0},
 'C4TMP': {'iemvar': 'c4tmpc', 'multiplier': 1.0},
 'C5TMP': {'iemvar': 'c5tmpc', 'multiplier': 1.0},
 'PPCTB': {'iemvar': 'phour', 'multiplier': 1.0}
}

def updateArchive(db, stationID):

  # Loop over all times
  for ts in db.keys():
    data = {}
    for v in mapping.keys():
      data[ mapping[v]['iemvar'] ] = -99
    for v in db[ts].keys():
      if (mapping.has_key(v)):
        data[mapping[v]['iemvar']] = float(db[ts][v]) * mapping[v]['multiplier']

    if (not data.has_key('tmpc')): 
      print data, ts, 'TMPC'
      continue
    if (not data.has_key('c1tmpc')): 
      print data, ts, 'C1'
      continue
    if (not data.has_key('c5tmpc')): 
      print data, ts, 'C5'
      continue
    if (data['tmpc'] < -50 or data['tmpc'] > 120):
      return
    if (data['relh'] < 1 or data['relh'] > 100):
      return
    data['tmpf'] = mesonet.c2f(data['tmpc'])
    data['dwpf'] = mesonet.dwpf(data['tmpf'], data['relh'])
    data['c1tmpf'] = mesonet.c2f(data['c1tmpc'])
    data['c2tmpf'] = mesonet.c2f(data['c2tmpc'])
    data['c3tmpf'] = mesonet.c2f(data['c3tmpc'])
    data['c4tmpf'] = mesonet.c2f(data['c4tmpc'])
    data['c5tmpf'] = mesonet.c2f(data['c5tmpc'])
    #dbts = ts + mx.DateTime.RelativeDateTime(hours=-1)
    dbts = ts
    data['valid'] = dbts.strftime("%Y-%m-%d %H:%M")
    data['year'] = ts.strftime("%Y")
    data['station'] = stationID

    sql = "DELETE from t%(year)s_hourly WHERE station = '%(station)s' and \
      valid = '%(valid)s'" % data
    mydb.query(sql)
    sql = "INSERT into t%(year)s_hourly (station, valid, tmpf, dwpf, srad, \
     sknt, drct, relh, pres, c1tmpf, c2tmpf, c3tmpf, c4tmpf, c5tmpf, \
     c1smv, c2smv, c3smv, c4smv, c5smv, phour) \
     VALUES \
    ('%(station)s', '%(valid)s', '%(tmpf)s', '%(dwpf)s', '%(srad)s','%(sknt)s',\
     '%(drct)s', '%(relh)s', '%(pres)s', '%(c1tmpf)s', '%(c2tmpf)s', \
     '%(c3tmpf)s', '%(c4tmpf)s', '%(c5tmpf)s', '%(c1smv)s', '%(c2smv)s', \
     '%(c3smv)s', '%(c4smv)s', '%(c5smv)s', '%(phour)s')" % data
    #print sql
    mydb.query(sql)


def updateIEMAccess(db, stationID):
  keys = db.keys()
  keys.sort()
  
  if (len(keys) < 2):
    return
  ts = keys[-1]
#  print db[keys[-1]].keys()
  if (stationID == "S2047" and not db[ts].has_key("c1smv") ):
     ts = keys[-2]

  # Make sure this ob is not over a day old
  now = mx.DateTime.now()
  if (now > (ts + mx.DateTime.RelativeDateTime(days=+1) )):
    return
   #
   # This is caused by a short data file where the first section
   # will have an ob, but the others won't.  Just another quirk
   #
  if (not db[ts].has_key("C1SMV") ): 
    #print db[ts].keys()
    return
  if (not db[ts].has_key("C5SMV") ): 
    #print db[ts].keys()
    return

  iem = iemAccessOb.iemAccessOb(stationID, "SCAN")
  #iem.data['ts'] = ts + mx.DateTime.RelativeDateTime(hours=-1)
  iem.data['ts'] = ts
  iem.data['year'] = ts.year

  for v in mapping.keys():
    iem.data[ mapping[v]['iemvar'] ] = -99
  for v in db[ts].keys():
    if (mapping.has_key(v)):
      iem.data[mapping[v]['iemvar']] = float(db[ts][v]) * mapping[v]['multiplier']

  iem.data['tmpf'] = mesonet.c2f(iem.data['tmpc'])
  if (iem.data['tmpf'] < -50 or iem.data['tmpf'] > 120):
    return
  if (iem.data['relh'] < 1 or iem.data['relh'] > 100):
    return
  iem.data['dwpf'] = mesonet.dwpf(iem.data['tmpf'], iem.data['relh'])
  iem.data['dwpf'] = mesonet.dwpf(iem.data['tmpf'], iem.data['relh'])
  iem.data['c1tmpf'] = mesonet.c2f(db[ts]['C1TMP'])
  iem.data['c2tmpf'] = mesonet.c2f(db[ts]['C2TMP'])
  iem.data['c3tmpf'] = mesonet.c2f(db[ts]['C3TMP'])
  iem.data['c4tmpf'] = mesonet.c2f(db[ts]['C4TMP'])
  iem.data['c5tmpf'] = mesonet.c2f(db[ts]['C5TMP'])
  iem.updateDatabase(iemdb)
  if (iem.error != 0):
    print iem.sql

stations = [
 ['ia', 2068],
 ['ia', 2031],
 ['mo', 2047],
 ['ne', 2001],
 ['il', 2004],
]

def Main():
  now = mx.DateTime.now()
  for (state, sid) in stations:
    db = {}
    fp = "ftp://ftp.wcc.nrcs.usda.gov/data/scan/%s/%s/%s_%s.txt" %(
         state, sid, sid, now.strftime("%Y%m%d"))
    try:
      lines = urllib2.urlopen( fp ).readlines()
    except IOError:
      print 'Download FAIL: %s' % (fp,)
      continue
    for line in lines:
      if (len(line) < 10): continue
      if (line[:4] == "Date"):
        fields = re.split("\s+", line[14:])
        continue
    
      if line[0] in ["0","1"]:  # Timestamp!
        ts = mx.DateTime.strptime(line[:10], "%y%m%d%H%M")
        if (not db.has_key(ts)): db[ts] = {}
        for c in range(len(fields)):
          e = 19 + (c*7)
          s = e - 7
          db[ts][ fields[c].upper() ] = line[s:e]

    updateIEMAccess(db, "S%s" % (sid,) )
    updateArchive(db, "%s" % (sid,) )
Main()
