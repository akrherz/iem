

import os, mx.DateTime, pg
iemdb = pg.connect("iem", "iemdb", user="nobody")

rs = iemdb.query("SELECT station from current WHERE network = 'KCCI' and \
  valid > 'TODAY' and station != 'SCEI4' ORDER by pday DESC").dictresult()
dict = {}
dict['timestamp'] = mx.DateTime.now()
dict['sid1'] = rs[0]['station']
dict['sid2'] = rs[1]['station']
dict['sid3'] = rs[2]['station']
dict['sid4'] = rs[3]['station']
dict['sid5'] = rs[4]['station']
dict['q'] = "%Q"

out = open('top5rain.scn', 'w')

out.write( open('top5rain.tpl','r').read() % dict )

out.close()

os.system("/home/ldm/bin/pqinsert top5rain.scn")
os.remove("top5rain.scn")
