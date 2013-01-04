"""
 Send the current_log history of SNET observations to its long term home

 The database partitioning is based on monthly tables based on UTC Time, so 
 this runs at 0z and takes the previous GMT day...

"""

import datetime
import os
import iemdb
import iemtz
import psycopg2.extras
import subprocess
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
SNET = iemdb.connect('snet')
scursor = SNET.cursor(cursor_factory=psycopg2.extras.DictCursor)

utc = datetime.datetime.utcnow()
utc = utc.replace(tzinfo=iemtz.UTC())
# We want 0z today
ets = utc.replace(hour=0,minute=0,second=0,microsecond=0)
# 0z yesterday
sts = ets - datetime.timedelta(days=1)

# Collect obs from iemaccess
sql = """SELECT c.*, t.id from current_log c JOIN stations t 
    ON (t.iemid = c.iemid) WHERE valid >= %s and valid < %s and 
    t.network IN ('KELO','KCCI','KIMT')"""
args = (sts, ets)
icursor.execute(sql, args)

# Dump them into snet archive...
"""
 station | character varying(5)     | 
 valid   | timestamp with time zone | 
 tmpf    | smallint                 | 
 dwpf    | smallint                 | 
 drct    | smallint                 | 
 sknt    | real                     | 
 pday    | real                     | 
 pmonth  | real                     | 
 srad    | real                     | 
 relh    | real                     | 
 alti    | real                     | 
 gust    | smallint                 | 
"""

def formatter(val, precision):
    if val is None or type(val) == type('s'):
        return 'None'
    fmt = '%%.%sf' % (precision,)
    return fmt % val

out = open('/tmp/snet_dbinsert.sql', 'w')
out.write("DELETE from t%s WHERE valid >= '%s' and valid < '%s';\n" % (
                    sts.strftime("%Y_%m"), sts, ets ))
out.write("COPY t%s FROM stdin WITH NULL 'None';\n" % (sts.strftime("%Y_%m"),) )
i = 0
for row in icursor:
    if (row['pmonth'] is None):
        row['pmonth'] = 0
    try:
        s = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                row.get('id'), row.get('valid'), 
                formatter(row.get('tmpf'), 0), formatter(row.get('dwpf'), 0),
                formatter(row.get('drct'), 0), row.get('sknt'), row.get('pday'),
                row.get('pmonth'), row.get('srad'), row.get('relh'),
                row.get('pres'), formatter(row.get('gust'),0) )
    except:
        print 'Fail', row
    out.write(s)
    if i > 0 and i % 1000 == 0:
        out.write("\.\nCOPY t%s FROM stdin WITH NULL 'None';\n" % (
                                                    sts.strftime("%Y_%m"),) )
    i += 1
out.write("\.\n")
out.close()

proc = subprocess.Popen("psql -h iemdb -f /tmp/snet_dbinsert.sql snet",
                        shell=True, stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
output = proc.stderr.read().replace("DELETE 0\n","")
if len(output) > 0:
    print 'Error encountered with dbinsert...'
    print output
# Clean up after ourself
os.unlink('/tmp/snet_dbinsert.sql')
