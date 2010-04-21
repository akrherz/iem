
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
      ts.strftime("%Y-%m-%d"), networks)
rs = iemdb.query(sql).dictresult()

for i in range(len(rs)):
  sql = """INSERT into t%s (station, valid, tmpf, dwpf, drct, sknt, tfs0,
    tfs1, tfs2, tfs3, subf, gust, tfs0_text, tfs1_text, tfs2_text, tfs3_text,
    pcpn, vsby)
    values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s',%s,%s
    )""" % (
   ts.year,rs[i]['station'], rs[i]['valid'], (rs[i]['tmpf']), 
  (rs[i]['dwpf']), (rs[i]['drct']), (rs[i]['sknt']),
   rs[i]['tfs0'],
   rs[i]['tfs1'],
   rs[i]['tfs2'],
   rs[i]['tfs3'],
   rs[i]['subf'],
   rs[i]['gust'],
  (rs[i]['tfs0_text'] or "Null"), 
  (rs[i]['tfs1_text'] or "Null"), 
  (rs[i]['tfs2_text'] or "Null"), 
  (rs[i]['tfs3_text'] or "Null"), 
   rs[i]['pday'],
   rs[i]['vsby']
   )
  try:
    rwis.query(sql)
  except:
    print sql
    traceback.print_exc(file=sys.stdout)
