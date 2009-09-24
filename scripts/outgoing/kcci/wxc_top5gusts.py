
from pyIEM import iemAccessDatabase
import os
iemdb = iemAccessDatabase.iemAccessDatabase()

rs = iemdb.query("SELECT station from current WHERE network = 'KCCI' and \
  valid > 'TODAY' and station != 'SLOI4' ORDER by gust DESC").dictresult()
dict = {}
dict['sid1'] = rs[0]['station']
dict['sid2'] = rs[1]['station']
dict['sid3'] = rs[2]['station']
dict['sid4'] = rs[3]['station']
dict['sid5'] = rs[4]['station']

out = open('top5gusts.scn', 'w')

out.write( open('top5_gusts.tpl','r').read() % dict )

out.close()

os.system("/home/ldm/bin/pqinsert top5gusts.scn")
os.remove("top5gusts.scn")
