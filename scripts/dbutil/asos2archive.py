"""
 Dump ASOS observations into the long term archive...

 Database paritioning is now based on the UTC day, so we need to make sure
 we are not inserting where we should not be
"""
import datetime
import sys
import iemdb
import iemtz
import psycopg2.extras
ASOS = iemdb.connect('asos')
IEM = iemdb.connect('iem')
acursor = ASOS.cursor()
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

utc = datetime.datetime.utcnow()
utc = utc.replace(tzinfo=iemtz.UTC())
    
sts = utc.replace(hour=0,minute=0,second=0,microsecond=0)

# Option 1 is to run for 'today' and for Iowa data    
if len(sys.argv) > 1:
    ets = utc
    networks = "(network = 'IA_ASOS' or network = 'AWOS')"
# Option 2 is to run for 'yesterday' and for the entire archive
else:
    ets = sts 
    sts = sts - datetime.timedelta(days=1)
    networks = "(network ~* 'ASOS' or network ~* 'AWOS')"

# Delete any obs from yesterday
sql = "DELETE from t%s WHERE valid >= '%s' and valid < '%s'" % (sts.year, 
                                                                sts, ets )
acursor.execute(sql)

# Get obs from Access
sql = """SELECT c.*, t.network, t.id from 
    current_log c JOIN stations t on (t.iemid = c.iemid) WHERE 
    valid >= %s and valid < %s and """+networks+"""
    """ 
args = (sts, ets)
icursor.execute(sql, args)
for row in icursor:
    sql = """INSERT into t"""+ str(sts.year) +""" (station, valid, tmpf, dwpf, drct, sknt,  alti, 
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
