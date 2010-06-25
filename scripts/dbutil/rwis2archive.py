
from pyIEM import iemdb
import mx.DateTime, sys, traceback
i = iemdb.iemdb()
rwis = i['rwis']
iemdb = i['iem']

# Hack it for today, just fuss with iowa
if (len(sys.argv) > 1):
  ts = mx.DateTime.now()
else:
  ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

# Delete any obs from yesterday
sql = "DELETE from t%s WHERE date(valid) = '%s'" % (ts.year, 
       ts.strftime("%Y-%m-%d") )
rwis.query(sql)

# Get obs from Access
sql = """SELECT * from current_log WHERE date(valid) = '%s' 
      and network = 'IA_RWIS'""" % (
      ts.strftime("%Y-%m-%d"), )
rs = iemdb.query(sql).dictresult()

for i in range(len(rs)):
  sql = """INSERT into t%s (station, valid, tmpf, dwpf, drct, sknt, tfs0,
    tfs1, tfs2, tfs3, subf, gust, tfs0_text, tfs1_text, tfs2_text, tfs3_text,
    pcpn, vsby)
    values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s',%s,%s
    )""" % (
   ts.year,rs[i]['station'], rs[i]['valid'], 
  (rs[i]['tmpf'] or "Null"), 
  (rs[i]['dwpf'] or "Null"), 
  (rs[i]['drct'] or "Null"), 
  (rs[i]['sknt'] or "Null"),
   rs[i]['tsf0'] or "Null",
   rs[i]['tsf1'] or "Null",
   rs[i]['tsf2'] or "Null",
   rs[i]['tsf3'] or "Null",
   rs[i]['rwis_subf'] or "Null",
   rs[i]['gust'] or "Null",
  (rs[i]['scond0'] or "Null"), 
  (rs[i]['scond1'] or "Null"), 
  (rs[i]['scond2'] or "Null"), 
  (rs[i]['scond3'] or "Null"), 
   rs[i]['pday'] or "Null",
   rs[i]['vsby'] or "Null"
   )
  try:
    rwis.query(sql)
  except:
    print sql
    traceback.print_exc(file=sys.stdout)
