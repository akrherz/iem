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
current = {}

def make_time( year, month, day, hhmm ):
    """ Convert strings from file into a proper timestamp """
    hhmm = hhmm.strip()
    ts = mx.DateTime.DateTime(int(year), int(month), int(day))
    if hhmm == '2400':
        hhmm == '0000'
        ts += mx.DateTime.RelativeDateTime(days=1)
    ts += mx.DateTime.RelativeDateTime(hour=int(hhmm[:-2]))
    return ts

def initdb(fn):
    """
    Initialize the observation dataset based on the filename provided 
    and some snooping...
    """
    fname = re.split("/", fn)[-1]
    ts = mx.DateTime.strptime(fname, "D%d%b%y.TXT")
    # The default file contains data for the past 2 days and a few hours
    # for today.
    ets = ts + mx.DateTime.RelativeDateTime(hour=2)

    # Lets sample the second line to get the start time
    lines = open(fn).readlines()
    tokens = lines[1].split(",")
    sts = make_time( tokens[2], tokens[0], tokens[1], tokens[3])
    sts += mx.DateTime.RelativeDateTime(hour=0)

    # Initialize the obs database
    for id in nt.sts.keys():
        obs[id] = {}
        current[id] = {}
    now = sts
    interval = mx.DateTime.RelativeDateTime(hours=+1)
    while now <= ets:
        for id in nt.sts.keys():
            obs[id][now.strftime("%Y-%m-%d %H:%M")] = {}
            current[id][now.strftime("%Y-%m-%d %H:%M")] = {}
        now = now + interval

    return sts, ets

def load_data(sts, ets):
    """ Go into the database and get what we already have stored """
    rs = mydb.query("""SELECT * from hourly WHERE
        valid >= '%s' and valid < '%s'""" % (sts.strftime("%Y-%m-%d %H:%M"),
                                             ets.strftime("%Y-%m-%d %H:%M"))
                    ).dictresult()
    for i in range(len(rs)):
        station = rs[i]['station']
        if not current.has_key(station):
            continue
        for key in rs[i].keys():
            val = str(rs[i][key])
            if rs[i][key] is None:
                val = None
            current[station][ rs[i]['valid'][:16] ][key] = val
        
    rs = mydb.query("""SELECT * from daily WHERE
        valid >= '%s' and valid <= '%s'""" % (sts.strftime("%Y-%m-%d"),
                                             ets.strftime("%Y-%m-%d"))
                    ).dictresult()
    for i in range(len(rs)):
        station = rs[i]['station']
        if not current.has_key(station):
            continue
        for key in rs[i].keys():
            val = str(rs[i][key])
            if rs[i][key] is None:
                val = None
            current[station][ rs[i]['valid'] +" 00:00" ][key] = val
   
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
            ts = make_time( tokens[2], tokens[0], tokens[1], tokens[3])
           
        if ts < e:
            tstring = ts.strftime("%Y-%m-%d %H:%M")
            for i in range(len(dcols)):
                if not obs.has_key(stationID) or not obs[stationID].has_key(tstring):
                    continue
                val = tokens[4+i].strip()
                if val == "":
                    val = None
                try:
                    obs[stationID][tstring][ dcols[i] ] = val
                except:
                    print stationID, dcols, i, val
      

def prepareDB(s,e):
    dayOne = s.strftime("%Y-%m-%d")
    dayTwo = (s + mx.DateTime.RelativeDateTime(days=+1) ).strftime("%Y-%m-%d")

    sql = "DELETE from daily WHERE valid IN ('%s','%s')" % (dayOne, dayTwo) 
    mydb.query(sql)

    sql = """DELETE from hourly WHERE valid > '%s' and valid < '%s 23:59' 
    """ % ( dayOne, e.strftime("%Y-%m-%d"))
    mydb.query(sql)

def compare_equal(station, tstring):
    """ Compare the database to what we have here """
    if not current.has_key(station):
        return False
    if not current[station].has_key(tstring):
        return False
    for key in obs[station][tstring].keys():
        if (obs[station][tstring][key] is None and 
            current[station][tstring].get(key, -9999) is None):
            continue 
        if key.find("_") == -1 and current[station][tstring].get(key, None) is not None:
            if float(obs[station][tstring][key]) == float(current[station][tstring].get(key, -9999)):
                continue
        if obs[station][tstring][key] != current[station][tstring].get(key, -9999):
            #print 'MISS', station, tstring, key, obs[station][tstring][key], current[station][tstring].get(key, -9999)
            return False
    return True

def insertData(s, e):
    """
    Actually put the data to the database, gasp!
    """
    ds = 0
    hs = 0
    skips = 0
    for stid in obs.keys():
        for tstring in obs[stid].keys():
            if compare_equal(stid, tstring):
                skips += 1
                continue
            d = obs[stid][tstring]
            #print stid, ts.strftime("%Y-%m-%d %H:%M:00-0600"), d.keys()
            if d.has_key('c11') : # Daily Value
                d['valid'] = tstring
                d['station'] = stid
                mydb.query("""DELETE from daily where station = '%s' and
                valid = '%s' """ % (stid, d['valid']))
                #try:
                ds += 1
                mydb.insert("daily", d)
                #except:
                #    continue

            if d.has_key('c100'): # We can insert both daily and hourly vals
                d['valid'] = tstring + ":00-0600"
                d['station'] = stid
                mydb.query("""DELETE from hourly where station = '%s' and
                valid = '%s' """ % (stid, d['valid']))
                #try:
                hs += 1
                mydb.insert("hourly", d)
                #except:
                #    continue

    print 'DB Daily Inserts: %s Hourly Inserts: %s Skips: %s' % (ds, hs, skips)

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
        ob = obs[stid][now.strftime("%Y-%m-%d %H:%M")]
        output.write(fmt % (nt.sts[stid]['name'], ob.get('c11_f', 'NA'), 
                ob.get('c12_f', 'NA'), ob.get('c20_f', 'NA'), 
                ob.get('c30_f', 'NA'), ob.get('c40_f', 'NA'), 
                ob.get('c80_f', 'NA'), ob.get('c90_f', 'NA'), 
                ob.get('c70_f', 'NA'), ob.get('c90', 'NA') ) )


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

if __name__ == '__main__':
    # Get the filename we are to process
    f = sys.argv[1]
    # Figure out the start and end times found in the file...
    s, e = initdb(f)
    process(f, s, e)
    load_data(s, e)
    #prepareDB(s, e)
    insertData(s, e)
    printReport(e)
