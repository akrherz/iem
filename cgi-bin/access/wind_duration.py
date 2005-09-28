#!/mesonet/python/bin/python
# Compute Wind Durations

import iemAccess, mx.DateTime, stationTable
st = stationTable.stationTable("/mesonet/TABLES/iowa.stns")

def Main():
  rs = iemAccess.iemdb.query("SELECT station, valid, sknt from current_log \
    WHERE network IN ('IA_ASOS','AWOS') and local_date(valid) = 'YESTERDAY' ORDER by \
    valid ASC").dictresult()

  db = {}
  lastOb = {}
  for id in st.ids:
    db[id] = {}
    lastOb[id] = mx.DateTime.today()
    for wnd in (10,20,30,40,50):
      db[id][wnd] = {'lastts': 0, 'cduration': 0, 'lduration': 0}

  badStations = {}
  for i in range(len(rs)):
    station = rs[i]['station']
    if (badStations.has_key(station)):
       continue
    sknt = int(rs[i]['sknt'])
    valid = mx.DateTime.strptime(rs[i]['valid'][:16], "%Y-%m-%d %H:%M") 
    lob = lastOb[station]
    if ((valid - lob) > 4000):
      badStations[station] = 1
    if (valid == lob):
      continue
    lastOb[station] = valid
    for wnd in (10,20,30,40,50):
      if (sknt >= wnd):  #Threshold Exceeded
        lastts = db[station][wnd]['lastts'] # Last Ob
        if (lastts == 0): # Nothing prior
          db[station][wnd]['lastts'] = valid
        else: # We have a duration
          addDuration = (valid - lob)
          db[station][wnd]['cduration'] += addDuration
          if (db[station][wnd]['cduration'] > db[station][wnd]['lduration']):
             db[station][wnd]['lduration'] = db[station][wnd]['cduration']
      else:
        db[station][wnd]['lastts'] = 0
        db[station][wnd]['cduration'] = 0

  print "%5s %5s %5s %5s %5s %5s" % ("SID", ">=10", ">=20", ">=30", ">=40", ">=50")
  for sid in db.keys():
    if (badStations.has_key(sid)):
      print "Site %s missing data for 1 hour +" % (sid, )
    else:
      print "%5s %5.1f %5.1f %5.1f %5.1f %5.1f" % (sid, \
      (db[sid][10]['lduration'])/3600.0, \
      (db[sid][20]['lduration'])/3600.0, \
      (db[sid][30]['lduration'])/3600.0, \
      (db[sid][40]['lduration'])/360.0, \
      (db[sid][50]['lduration'])/3600.0 )

Main()
