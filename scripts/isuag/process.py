"""
Process the raw file (argument #1) into the IEM database
"""
import re
import string
import mx.DateTime
import string
import sys
import traceback
import network
nt = network.Table("ISUAG")
import pg
mydb = pg.DB('isuag', 'iemdb')
mydb.query("SET TIME ZONE 'CST6'")

obs = {}

def initdb(fn):
    """
    Initialize the observation dataset based on the filename provided and some
    knowledge on what data should reside in that file!
    """
    fname = re.split("/", fn)[-1]
    ts = mx.DateTime.strptime(fname, "D%d%b%y.TXT")
    # The default file contains data for the past 2 days and a few hours
    # for today.
    s = ts + mx.DateTime.RelativeDateTime(days=-3)
    e = ts

    for id in nt.sts.keys():
        obs[id] = {}

    now = s 
    interval = mx.DateTime.RelativeDateTime(hours=+1)
    while now <= e:
        for id in nt.sts.keys():
            obs[id][now] = {}
        now = now + interval

    return s, e

def process(fn, s, e):
    """
    Actually process the file! 
    """
    lines = open(fn, 'r').readlines()
    for line in lines:
        if (line[0] == "*"):
            stationID = string.upper(line[3:10])
            dc = re.split(",", line)[1:-1]
            dcols = []
            for c in dc:
                dcols.append("c"+ string.strip(c))
                dcols.append("c"+ string.strip(c) +"_f")
            continue
        tokens = re.split(",", line)
        if len(tokens) < 4:
            break
        ts = mx.DateTime.DateTime(int(tokens[2]), int(tokens[0]), int(tokens[1]))
        # If this row is an hourly ob
        if int(dc[0]) == 100:
            hr = int(tokens[3]) / 100
            if (hr == 24):
                hr = 0
                ts += mx.DateTime.RelativeDateTime(days=1)
            ts += mx.DateTime.RelativeDateTime(hour=hr)
      
        if ts < e:
            for i in range(len(dcols)):
                if not obs.has_key(stationID) or not obs[stationID].has_key(ts):
                    continue
                try:
                    obs[stationID][ts][ dcols[i] ] = tokens[4+i]
                except:
                    print stationID, dcols, i
      

def prepareDB(s,e):
    dayOne = s.strftime("%Y-%m-%d")
    dayTwo = (s + mx.DateTime.RelativeDateTime(days=+1) ).strftime("%Y-%m-%d")

    sql = "DELETE from daily WHERE valid IN ('%s','%s')" % (dayOne, dayTwo) 
    mydb.query(sql)

    sql = """DELETE from hourly WHERE valid >= '%s' and valid < '%s 23:59' 
    """ % ( dayOne, e.strftime("%Y-%m-%d"))
    mydb.query(sql)


def insertData(s, e):
    """
    Actually put the data to the database, gasp!
    """
    for stid in obs.keys():
        for ts in obs[stid].keys():
            d = obs[stid][ts]
            if ts > e:
                continue
                #print stid, ts.strftime("%Y-%m-%d %H:%M:00-0600"), d.keys()
            if (d.has_key('c11') ): # Daily Value
                d['valid'] = ts.strftime("%Y-%m-%d")
                d['station'] = stid
                try:
                    mydb.insert("daily", d)
                except:
                    continue

            if (d.has_key('c100') ): # We can insert both daily and hourly vals
                d['valid'] = ts.strftime("%Y-%m-%d %H:%M:00-0600")
                d['station'] = stid
                try:
                    mydb.insert("hourly", d)
                except:
                    continue

def printReport(ts):
    """
    Create a quasi useful report that we can send to folks interested in 
    the flags generated on the data...
    """
    now = ts + mx.DateTime.RelativeDateTime(days=-1, hour=0)
    output = open('report.txt', 'w')

    output.write("""

  ISU AgClimate Daily Data Report  (%s)
  ---------------------------------------------
""" % (now.strftime("%b %d, %Y")) )

    fmt = "%-15s %4s %4s %4s %4s %4s %4s %4s %4s %4s\n"
    output.write(fmt % ('','c11','c12','c20','c30','c40','c80','c90','c70','Rain'))
    ids = obs.keys()
    ids.sort()
    for stid in ids:
        ob = obs[stid][now]
        output.write(fmt % (nt.sts[stid]['name'], ob,get('c11_f', 'NA'), 
                ob.get('c12_f', 'NA'), ob.get('c20_f', 'NA'), 
                ob.get('c30_f', 'NA'), ob.get('c40_f', 'NA'), 
                ob.get('c80_f', 'NA'), ob.get('c90_f', 'NA'), 
                ob.get('c70_f', 'NA'), ob.get('c90', 'NA').strip() ) )


    output.write("""

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
    output.close()

def Main():
    f = sys.argv[1]
    s, e = initdb(f)
    process(f, s, e)
    prepareDB(s, e)
    insertData(s, e)
    printReport(e)
Main()
