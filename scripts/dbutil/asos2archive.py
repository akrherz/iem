
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
sql = """SELECT c.*, t.network, t.id from current_log c, stations t WHERE date(valid) = '%s' 
      and %s and (t.network ~* 'ASOS' or t.network ~* 'AWOS')
      and t.iemid = c.iemid""" % (
      ts.strftime("%Y-%m-%d"), networks)
rs = iemdb.query(sql).dictresult()

# Fire them into Archive
#print len(rs)
for i in range(len(rs)):
  #if ((i%1000)==0): print i

  sql = """INSERT into t%s (station, valid, tmpf, dwpf, drct, sknt,  alti, 
    p01i, gust, vsby, skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, metar,
    p03i, p06i, p24i, max_tmpf_6hr, min_tmpf_6hr, max_tmpf_24hr, min_tmpf_24hr,
    mslp) 
    values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s',%s,%s,%s,%s,'%s',
    %s,%s,%s,%s,%s,%s,%s,%s)""" % (
  ts.year,rs[i]['id'], rs[i]['valid'], 
  valcheck(rs[i]['tmpf']), 
  valcheck(rs[i]['dwpf']), 
  valcheck(rs[i]['drct']), 
  valcheck(rs[i]['sknt']),
  valcheck(rs[i]['alti']), valcheck(rs[i]['phour']), 
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
  rs[i]['raw'],
  valcheck(rs[i]['p03i']),
  valcheck(rs[i]['p06i']),
  valcheck(rs[i]['p24i']),
  valcheck(rs[i]['max_tmpf_6hr']),
  valcheck(rs[i]['min_tmpf_6hr']),
  valcheck(rs[i]['max_tmpf_24hr']),
  valcheck(rs[i]['min_tmpf_24hr']),
  valcheck(rs[i]['pres'])
)
  try:
    asos.query(sql)
  except:
    print sql
    traceback.print_exc(file=sys.stdout)
