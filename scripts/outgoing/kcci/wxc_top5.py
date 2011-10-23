

import os, mx.DateTime, pg, sys, tempfile
iemdb = pg.connect("iem", "iemdb", user="nobody")

rs = iemdb.query("SELECT t.id as station from current c, stations t WHERE t.network = 'KCCI' and \
  t.iemid = c.iemid and valid > 'TODAY' and t.id not in ('SCEI4','SWII4', 'SKCI4') ORDER by pday DESC").dictresult()
dict = {}
if len(rs) < 5:
  sys.exit(0)

dict['timestamp'] = mx.DateTime.now()
dict['sid1'] = rs[0]['station']
dict['sid2'] = rs[1]['station']
dict['sid3'] = rs[2]['station']
dict['sid4'] = rs[3]['station']
dict['sid5'] = rs[4]['station']

fd, path = tempfile.mkstemp()
os.write(fd,  open('top5rain.tpl','r').read() % dict )
os.close(fd)

os.system("/home/ldm/bin/pqinsert -p 'auto_top5rain.scn' %s" % (path,))
os.remove(path)

