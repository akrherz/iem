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
now = mx.DateTime.now()

icursor.execute("""SELECT s.id as station from summary_%s c, stations s WHERE 
  s.network = 'KCCI' and s.iemid = c.iemid and 
  day = 'TODAY'  ORDER by max_tmpf DESC""" % (now.year, ))
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
os.write(fd,  open('top5highs.tpl','r').read() % dict )
os.close(fd)

subprocess.call("/home/ldm/bin/pqinsert -p 'auto_top5highs.scn' %s" % (path,),
                shell=True)
os.remove(path)
