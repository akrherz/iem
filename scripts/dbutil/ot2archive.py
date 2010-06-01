
from pyIEM import iemdb
import mx.DateTime, sys, traceback
i = iemdb.iemdb()
other = i['other']
iemdb = i['iem']

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

# Delete any obs from yesterday
sql = "DELETE from t%s WHERE date(valid) = '%s'" % (ts.year, 
      ts.strftime("%Y-%m-%d") )
other.query(sql)

# Get obs from Access
sql = "SELECT * from current_log WHERE date(valid) = '%s' and network = 'OT'" % (ts.strftime("%Y-%m-%d"), )
rs = iemdb.query(sql).dictresult()

for i in range(len(rs)):
  pday = 0
  if (rs[i]['pday'] is not None and float(rs[i]['pday']) > 0):
    pday = float(rs[i]['pday']) 
  alti = rs[i]['alti']
  if alti is None and rs[i]['mslp'] is not None:
    alti = rs[i]['mslp'] * .03 
  sql = """INSERT into t%s (station, valid, tmpf, dwpf, drct, sknt,  alti, 
         pday, gust, c1tmpf,srad) values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s)""" % \
  (ts.year,rs[i]['station'], rs[i]['valid'], (rs[i]['tmpf'] or "Null"), \
  (rs[i]['dwpf'] or "Null"), (rs[i]['drct'] or "Null"), (rs[i]['sknt'] or "Null"),\
  (alti or "Null"), pday, (rs[i]['gust'] or "Null") , 
   (rs[i]['c1tmpf'] or "Null"), (rs[i]['srad'] or "Null"))
  try:
    other.query(sql)
  except:
    print sql
    traceback.print_exc(file=sys.stdout)
