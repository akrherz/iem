

import os, mx.DateTime, pg
iemdb = pg.connect('iem', 'iemdb', user='nobody')

rs = iemdb.query("SELECT station from summary WHERE network = 'KCCI' and \
  day = 'TODAY' and station not in ('SCEI4','SWII4') ORDER by pmonth DESC").dictresult()
dict = {}
dict['dy'] = 31
dict['timestamp'] = mx.DateTime.now()
dict['sid1'] = rs[0]['station']
dict['sid2'] = rs[1]['station']
dict['sid3'] = rs[2]['station']
dict['sid4'] = rs[3]['station']
dict['sid5'] = rs[4]['station']
dict['q'] = "%Q"
dict['fn'] = "Month Precip"
dict['title'] = "%s RAINFALL" % (mx.DateTime.now().strftime("%B"),)


out = open('top5monthrain.scn', 'w')

out.write( open('top5rain2day.tpl','r').read() % dict )

out.close()


os.system("/home/ldm/bin/pqinsert top5monthrain.scn")
os.remove("top5monthrain.scn")
