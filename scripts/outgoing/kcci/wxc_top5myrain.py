
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

dy = int(sys.argv[1])
now = mx.DateTime.now()

icursor.execute("""SELECT s.id as station, sum(pday) as rain from summary_%s c, stations s 
  WHERE s.network = 'KCCI' and s.iemid = c.iemid and 
  day > '%s' and s.id not in ('SCEI4','SWII4') GROUP by station ORDER by rain DESC""" % ( 
            now.year, (now - mx.DateTime.RelativeDateTime(days= int(dy) )).strftime("%Y-%m-%d") ))
dict = {}

dict['timestamp'] = mx.DateTime.now()
i = 1
for row in icursor:
    row = icursor.fetchone()
    if i == 6:
        break
    if qc.get(row[0], {}).get('precip', False):
        continue
    dict['sid%s' % (i,)] = row[0]
    i += 1

dict['q'] = "%Q"
dict['fn'] = "Last %s Day Precip" % (dy,)
if dy == 2:
  dict['title'] = "TWO DAY RAINFALL"
if dy == 3:
  dict['title'] = "3 DAY RAINFALL"
if dy == 7:
  dict['title'] = "7 DAY RAINFALL"
if dy == 14:
  dict['title'] = "14 DAY RAINFALL"

fd, path = tempfile.mkstemp()
os.write(fd,  open('top5rainXday.tpl','r').read() % dict )
os.close(fd)

subprocess.call("/home/ldm/bin/pqinsert -p 'auto_top5rain_%sday.scn' %s" % (dy, path),
                shell=True)
os.remove(path)
