#!/usr/bin/env python
"""
Not sure if this is even used!
$Id: $:
"""
import sys
import psycopg2.extras
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import iemdb
WEPP = iemdb.connect('wepp', bypass=True)
wcursor = WEPP.cursor(cursor_factory=psycopg2.extras.DictCursor)

import cgi
import mx.DateTime
form = cgi.FormContent()
if form.has_key("d"):
  ts  = mx.DateTime.strptime(form['d'][0], '%Y-%m-%d')
else:
  ts  = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

print "Content-type: text/plain\n\n"
print "VALID,TWP,MIN_RUN,AVG_RUN,MAX_RUN,MIN_LOSS,AVG_LOSS,MAX_LOSS"
wcursor.execute("""SELECT * from results_by_twp WHERE 
     valid = '%s' ORDER by model_twp""" % (ts.strftime("%Y-%m-%d"),
     ))
for row in wcursor:
  print "%(valid)s,%(model_twp)s,%(min_runoff).4f,%(avg_runoff).4f,%(max_runoff).4f,%(min_loss).4f,%(avg_loss).4f,%(max_loss).4f" % row
