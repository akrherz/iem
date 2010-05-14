
import re, string, mx.DateTime, string, sys, traceback
from pyIEM import iemdb, stationTable
#i = iemdb.iemdb()
st = stationTable.stationTable("/mesonet/TABLES/campbellDB.stns")
#mydb = i['isuag']
import pg
mydb = pg.DB('isuag',host='iemdb')
mydb.query("SET TIME ZONE 'CST6'")


obs = {}

def initdb(fn):
  fname = re.split("/", fn)[-1]
  #print fname
  ts = mx.DateTime.strptime(fname, "D%d%b%y.TXT")
  # The default file contains data for the past 2 days and a few hours
  # for today.
  s = ts + mx.DateTime.RelativeDateTime(days=-2)
  e = ts

  for id in st.ids:
    obs[id] = {}

  now = s 
  interval = mx.DateTime.RelativeDateTime(hours=+1)
  while (now <= e):
    for id in st.ids:
      obs[id][now] = {}
    now = now + interval

  return s, e

def process(fn, s, e):
  lines = open(fn, 'r').readlines()
  for line in lines:
    if (line[0] == "*"):
      stationID = string.upper(line[3:10])
      dc = re.split(",", line)[1:-1]
      dcols = []
      for c in dc:
        dcols.append("c"+ string.strip(c))
        dcols.append("c"+ string.strip(c) +"_f")
#      print stationID, dcols
    else: # We have a data line!!!
      tokens = re.split(",", line)
      if (len(tokens) < 4):
        break
      ts = mx.DateTime.DateTime(int(tokens[2]), int(tokens[0]), int(tokens[1]))
      # If this row is an hourly ob
      if (int(dc[0]) == 100):
        hr = int(tokens[3]) / 100
        if (hr == 24):
          hr = 0
          ts += mx.DateTime.RelativeDateTime(days=1)
        ts += mx.DateTime.RelativeDateTime(hour=hr)
      
      if (ts < e):
        for i in range(len(dcols)):
          if (not obs[stationID].has_key(ts)):
            #print 'Why are we missing %s' % (ts,)
            continue
          obs[stationID][ts][ dcols[i] ] = tokens[4+i]
      

def prepareDB(s,e):
  dayOne = s.strftime("%Y-%m-%d")
  dayTwo = (s + mx.DateTime.RelativeDateTime(days=+1) ).strftime("%Y-%m-%d")

  sql = "DELETE from daily WHERE valid IN ('%s','%s')" % (dayOne, dayTwo) 
  mydb.query(sql)

  sql = "DELETE from hourly WHERE valid >= '%s' and valid < '%s 23:59' \
    " % ( dayOne, e.strftime("%Y-%m-%d"))
  mydb.query(sql)


def insertData(s, e):
  for stid in obs.keys():
    for ts in obs[stid].keys():
      d = obs[stid][ts]
      if (ts <= e):
        #print stid, ts.strftime("%Y-%m-%d %H:%M:00-0600"), d.keys()
        if (d.has_key('c11') ): # Daily Value
          d['valid'] = ts.strftime("%Y-%m-%d")
          d['station'] = stid
          mydb.insert("daily", d)

        if (d.has_key('c100') ): # We can insert both daily and hourly vals
          d['valid'] = ts.strftime("%Y-%m-%d %H:%M:00-0600")
          d['station'] = stid
          mydb.insert("hourly", d)

def printReport(ts):
  now = ts + mx.DateTime.RelativeDateTime(days=-1, hour=0)
  o = open('report.txt', 'w')

  o.write("""

  ISU AgClimate Daily Data Report  (%-10s)
  ---------------------------------------------
""" % (now.strftime("%b %d, %Y")) )

  fmt = "%-15s %4s %4s %4s %4s %4s %4s %4s %4s\n"
  o.write(fmt % ('','c11','c12','c20','c30','c40','c80','c90','c70'))
  for stid in obs.keys():
    ob = obs[stid][now]
    try:
      o.write(fmt % (st.sts[stid]['name'],ob['c11_f'],ob['c12_f'],ob['c20_f'],\
       ob['c30_f'], ob['c40_f'], ob['c80_f'], ob['c90_f'], ob['c70_f'] ) )
    except:
      continue

  o.write("""

Data Columns:              QC Flags:
  c11  High Temperature      M   The data is missing
  c12  Low Temperature       E   An instrument is flagged in error
  c20  Relative Humidity     R   Value is estimated
  c30  Soil Temperature      e   We are not confident of this estimate
  c40  Wind Velocity
  c70  Evapotranspiration
  c80  Solar Radiation
  c90  Precipitation
""")
  o.close()

def Main():
  f = sys.argv[1]
  s, e = initdb(f)
  process(f, s, e)
  prepareDB(s, e)
  insertData(s, e)
  printReport(e)
Main()
