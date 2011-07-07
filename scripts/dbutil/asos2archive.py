
from pyIEM import iemdb
import mx.DateTime, sys, traceback
i = iemdb.iemdb()
asos = i['asos']
iemdb = i['iem']

def valcheck(v):
    if v is None:
        return 'Null'
    return v

# Hack it for today, just fuss with iowa
if (len(sys.argv) > 1):
  ts = mx.DateTime.now()
  networks = "(network = 'IA_ASOS' or network = 'AWOS')"
else:
  ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
  networks = "(network ~* 'ASOS' or network ~* 'AWOS')"

# Delete any obs from yesterday
sql = "DELETE from t%s WHERE date(valid) = '%s'" % (ts.year, ts.strftime("%Y-%m-%d") )
asos.query(sql)

# Get obs from Access
sql = """SELECT * from current_log WHERE date(valid) = '%s' 
      and %s and (network ~* 'ASOS' or network ~* 'AWOS')""" % (
      ts.strftime("%Y-%m-%d"), networks)
rs = iemdb.query(sql).dictresult()

# Fire them into Archive
#print len(rs)
for i in range(len(rs)):
  #if ((i%1000)==0): print i
  p01m = 0
  if (rs[i]['phour'] is not None and float(rs[i]['phour']) > 0):
    p01m = float(rs[i]['phour']) * 25.4
  sql = """INSERT into t%s (station, valid, tmpf, dwpf, drct, sknt,  alti, 
    p01m, gust, vsby, skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, metar) 
    values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s',%s,%s,%s,%s,'%s')""" % (
  ts.year,rs[i]['station'], rs[i]['valid'], 
  valcheck(rs[i]['tmpf']), 
  valcheck(rs[i]['dwpf']), 
  valcheck(rs[i]['drct']), 
  valcheck(rs[i]['sknt']),
  valcheck(rs[i]['alti']), p01m, 
  valcheck(rs[i]['gust']), 
  valcheck(rs[i]['vsby']),
  (rs[i]['skyc1'] or ''),
  (rs[i]['skyc2'] or ''),
  (rs[i]['skyc3'] or ''),
  (rs[i]['skyc4'] or ''),
  valcheck(rs[i]['skyl1']),
  valcheck(rs[i]['skyl2']),
  valcheck(rs[i]['skyl3']), 
  valcheck(rs[i]['skyl4']),
  rs[i]['raw']
   )
  try:
    asos.query(sql)
  except:
    print sql
    traceback.print_exc(file=sys.stdout)
