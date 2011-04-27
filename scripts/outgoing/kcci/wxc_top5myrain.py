
import os, sys, mx.DateTime, pg, tempfile
iemdb = pg.connect('iem', 'iemdb', user='nobody')

dy = int(sys.argv[1])
now = mx.DateTime.now()

sql = "SELECT station, sum(pday) as rain from summary \
  WHERE network = 'KCCI' and \
  day > '%s' and station not in ('SCEI4','SWII4') GROUP by station ORDER by rain DESC" % \
 ( (now - mx.DateTime.RelativeDateTime(days= int(dy) )).strftime("%Y-%m-%d"), )

rs = iemdb.query(sql).dictresult()
dict = {}
dict['dy'] = dy
dict['sid1'] = rs[0]['station']
dict['sid2'] = rs[1]['station']
dict['sid3'] = rs[2]['station']
dict['sid4'] = rs[3]['station']
dict['sid5'] = rs[4]['station']
dict['timestamp'] = mx.DateTime.now()
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

os.system("/home/ldm/bin/pqinsert -p 'auto_top5rain_%sday.scn' %s" % (dy, path))
os.remove(path)