'''
 Generate top 5 rainfall reports scene for WXC
'''
import os
import subprocess
import datetime
import sys
import tempfile
import tracker
qc = tracker.loadqc()
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

icursor.execute("""SELECT t.id as station from current c, stations t 
  WHERE t.network = 'KCCI' and 
  t.iemid = c.iemid and valid > 'TODAY' ORDER by pday DESC""")
data = {}

data['timestamp'] = datetime.datetime.now()
i = 1
for row in icursor:
    if i == 6:
        break
    if qc.get(row[0], {}).get('precip', False):
        continue
    data['sid%s' % (i,)] = row[0]
    i += 1

if i == 1 or not data.has_key('sid5'):
    sys.exit()

fd, path = tempfile.mkstemp()
os.write(fd,  open('top5rain.tpl','r').read() % data )
os.close(fd)

subprocess.call("/home/ldm/bin/pqinsert -p 'auto_top5rain.scn' %s" % (path,),
                shell=True)
os.remove(path)

