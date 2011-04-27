
import os, mx.DateTime, pg, tempfile
iemdb = pg.connect('iem', 'iemdb', user='nobody')

rs = iemdb.query("SELECT station from summary WHERE network = 'KCCI' and \
  day = 'TODAY' and station != 'SAEI4' ORDER by max_tmpf DESC").dictresult()
dict = {}
dict['sid1'] = rs[0]['station']
dict['sid2'] = rs[1]['station']
dict['sid3'] = rs[2]['station']
dict['sid4'] = rs[3]['station']
dict['sid5'] = rs[4]['station']
dict['timestamp'] = mx.DateTime.now()


fd, path = tempfile.mkstemp()
os.write(fd,  open('top5highs.tpl','r').read() % dict )
os.close(fd)

os.system("/home/ldm/bin/pqinsert -p 'auto_top5highs.scn' %s" % (path,))
os.remove(path)
