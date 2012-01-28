"""
 Dump ASOS observations into the long term archive...
$Id: $:
"""
import mx.DateTime
import sys
import iemdb
import psycopg2.extras
ASOS = iemdb.connect('asos')
IEM = iemdb.connect('iem')
acursor = ASOS.cursor()
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Hack it for today, just fuss with iowa
if (len(sys.argv) > 1):
  ts = mx.DateTime.now()
  networks = "(network = 'IA_ASOS' or network = 'AWOS')"
else:
  ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
  networks = "(network ~* 'ASOS' or network ~* 'AWOS')"

# Delete any obs from yesterday
sql = "DELETE from t%s WHERE date(valid) = '%s'" % (ts.year, ts.strftime("%Y-%m-%d") )
acursor.execute(sql)

# Get obs from Access
sql = """SELECT c.*, t.network, t.id from current_log c, stations t WHERE date(valid) = '%s' 
      and %s and (t.network ~* 'ASOS' or t.network ~* 'AWOS')
      and t.iemid = c.iemid""" % (
      ts.strftime("%Y-%m-%d"), networks)
icursor.execute(sql)
for row in icursor:
    sql = """INSERT into t"""+ ts.year +""" (station, valid, tmpf, dwpf, drct, sknt,  alti, 
    p01i, gust, vsby, skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, metar,
    p03i, p06i, p24i, max_tmpf_6hr, min_tmpf_6hr, max_tmpf_24hr, min_tmpf_24hr,
    mslp, presentwx) 
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s,%s,%s,%s,%s,%s,%s,%s,%s)""" 

    args = (row['id'], row['valid'],  row['tmpf'], 
  row['dwpf'],  row['drct'],  row['sknt'],  row['alti'], row['phour'], 
  row['gust'], 
  row['vsby'],
  row['skyc1'] ,
  row['skyc2'] ,
  row['skyc3'] ,
  row['skyc4'] ,
  row['skyl1'],
  row['skyl2'],
  row['skyl3'], 
  row['skyl4'],
  row['raw'],
  row['p03i'],
  row['p06i'],
  row['p24i'],
  row['max_tmpf_6hr'],
  row['min_tmpf_6hr'],
  row['max_tmpf_24hr'],
  row['min_tmpf_24hr'],
  row['pres'],
  row['presentwx'])
  
    acursor.execute(sql, args)

if icursor.rowcount == 0:
    print 'Nothing done for asos2archive.py?'

icursor.close()
IEM.commit()
ASOS.commit()
ASOS.close()
IEM.close()