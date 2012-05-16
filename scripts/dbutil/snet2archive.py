"""
 Send the current_log history of SNET observations to its long term home
run from RUN_MIDNIGHT.sh
"""

import mx.DateTime
import os
import iemdb
import psycopg2.extras
import subprocess
IEM = iemdb.connect('iem')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
SNET = iemdb.connect('snet')
scursor = SNET.cursor(cursor_factory=psycopg2.extras.DictCursor)

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

# Collect obs from iemaccess
sql = """SELECT c.*, t.id from current_log c JOIN stations t 
    ON (t.iemid = c.iemid) WHERE date(valid) = '%s' and 
    t.network IN ('KELO','KCCI','KIMT')""" % (ts.strftime("%Y-%m-%d"),)
icursor.execute(sql)

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
out = open('/tmp/snet_dbinsert.sql', 'w')
out.write("DELETE from t%s WHERE date(valid) = '%s';\n" % (
                    ts.strftime("%Y_%m"), ts.strftime("%Y-%m-%d") ))
out.write("COPY t%s FROM stdin;\n" % (ts.strftime("%Y_%m"),) )
i = 0
for row in icursor:
    if (row['pmonth'] is None):
        row['pmonth'] = 0
    try:
        s = "%(id)s\t%(valid)s\t%(tmpf).0f\t%(dwpf).0f\t%(drct).0f\t%(sknt)s\t%(pday)s\t%(pmonth)s\t%(srad)s\t%(relh)s\t%(pres)s\t%(gust).0f\n" % row
    except:
        print 'Fail', row
    out.write(s.replace("None","null"))
    if i > 0 and i % 1000 == 0:
        out.write("\.\nCOPY t%s FROM stdin;\n" % (ts.strftime("%Y_%m"),) )
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
