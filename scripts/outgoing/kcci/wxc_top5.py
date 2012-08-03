

import os
import subprocess
import mx.DateTime
import sys
import tempfile
import tracker
qc = tracker.loadqc()
import iemdb
IEM = iemdb.connect("iem", bypass=True)
icursor = IEM.cursor()

icursor.execute("""SELECT t.id as station from current c, stations t 
  WHERE t.network = 'KCCI' and 
  t.iemid = c.iemid and valid > 'TODAY' ORDER by pday DESC""")
dict = {}

dict['timestamp'] = mx.DateTime.now()
i = 1
for row in icursor:
    row = icursor.fetchone()
    if i == 6:
        break
    if qc.get(row[0], {}).get('tmpf', False):
        continue
    dict['sid%s' % (i,)] = row[0]
    i += 1

fd, path = tempfile.mkstemp()
os.write(fd,  open('top5rain.tpl','r').read() % dict )
os.close(fd)

subprocess.call("/home/ldm/bin/pqinsert -p 'auto_top5rain.scn' %s" % (path,),
                shell=True)
os.remove(path)

