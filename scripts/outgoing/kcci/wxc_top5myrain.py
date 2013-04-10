
import os
import subprocess
import datetime
import sys
import tempfile
import tracker
qc = tracker.loadqc()
import iemdb
IEM = iemdb.connect("iem", bypass=True)
icursor = IEM.cursor()

dy = int(sys.argv[1])
now = datetime.datetime.now()

icursor.execute("""SELECT s.id as station, sum(pday) as rain from summary_%s c, stations s 
  WHERE s.network = 'KCCI' and s.iemid = c.iemid and 
  day > '%s' and s.id not in ('SCEI4','SWII4') GROUP by station ORDER by rain DESC""" % ( 
            now.year, (now - datetime.timedelta(days= int(dy) )).strftime("%Y-%m-%d") ))
data = {}

data['timestamp'] = now
i = 1
for row in icursor:
    if i == 6:
        break
    if qc.get(row[0], {}).get('precip', False):
        continue
    data['sid%s' % (i,)] = row[0]
    i += 1

data['q'] = "%Q"
data['fn'] = "Last %s Day Precip" % (dy,)
if dy == 2:
    data['title'] = "TWO DAY RAINFALL"
elif dy == 3:
    data['title'] = "3 DAY RAINFALL"
elif dy == 7:
    data['title'] = "7 DAY RAINFALL"
elif dy == 14:
    data['title'] = "14 DAY RAINFALL"

fd, path = tempfile.mkstemp()
os.write(fd,  open('top5rainXday.tpl','r').read() % data )
os.close(fd)

subprocess.call("/home/ldm/bin/pqinsert -p 'auto_top5rain_%sday.scn' %s" % (dy, path),
                shell=True)
os.remove(path)
