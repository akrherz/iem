# Mine SNET data, since we aren't writing flat files anymore!

import mx.DateTime, os
from pyIEM import iemdb
i = iemdb.iemdb()
access = i['iem']
snet = i['snet']

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

# Collect obs from iemaccess
sql = "SELECT c.*, t.id from current_log c JOIN stations t ON (t.iemid = c.iemid) WHERE date(valid) = '%s' and t.network IN ('KELO','KCCI','KIMT')" % (ts.strftime("%Y-%m-%d"),)
rs = access.query(sql).dictresult()

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
out.write("DELETE from t%s WHERE date(valid) = '%s';\n" % (ts.strftime("%Y_%m"), ts.strftime("%Y-%m-%d") ))
out.write("COPY t%s FROM stdin;\n" % (ts.strftime("%Y_%m"),) )
for i in range(len(rs)):
  if (rs[i]['pmonth'] is None):
    rs[i]['pmonth'] = 0
  s = "%(id)s\t%(valid)s\t%(tmpf)s\t%(dwpf)s\t%(drct)s\t%(sknt)s\t%(pday)s\t%(pmonth)s\t%(srad)s\t%(relh)s\t%(pres)s\t%(gust)s\n" % rs[i]
  out.write(s.replace("None","null"))
  if (i > 0 and i % 1000 == 0):
    out.write("\.\nCOPY t%s FROM stdin;\n" % (ts.strftime("%Y_%m"),) )

out.write("\.\n")
out.close()

so, si = os.popen4("psql -h iemdb -f /tmp/snet_dbinsert.sql snet")
