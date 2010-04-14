#!/mesonet/python/bin/python

from pyIEM import iemdb
i = iemdb.iemdb()
wepp = i['wepp']

import cgi, mx.DateTime
form = cgi.FormContent()
if form.has_key("d"):
  ts  = mx.DateTime.strptime(form['d'][0], '%Y-%m-%d')
else:
  ts  = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

print "Content-type: text/plain\n\n"
print "VALID,TWP,MIN_RUN,AVG_RUN,MAX_RUN,MIN_LOSS,AVG_LOSS,MAX_LOSS"
rs = wepp.query("""SELECT * from results_by_twp WHERE 
     valid = '%s' ORDER by model_twp""" % (ts.strftime("%Y-%m-%d"),
     )).dictresult()
for i in range(len(rs)):
  print "%(valid)s,%(model_twp)s,%(min_runoff).4f,%(avg_runoff).4f,%(max_runoff).4f,%(min_loss).4f,%(avg_loss).4f,%(max_loss).4f" % rs[i]
