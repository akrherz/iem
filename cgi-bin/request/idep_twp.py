#!/usr/bin/env python
"""
Not sure if this is even used!
"""
import cgi
import mx.DateTime
import psycopg2.extras
WEPP = psycopg2.connect(database='wepp', host='iemdb', user='nobody')
wcursor = WEPP.cursor(cursor_factory=psycopg2.extras.DictCursor)

form = cgi.FormContent()
if 'd' in form:
    ts = mx.DateTime.strptime(form['d'][0], '%Y-%m-%d')
else:
    ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)

print "Content-type: text/plain\n\n"
print "VALID,TWP,MIN_RUN,AVG_RUN,MAX_RUN,MIN_LOSS,AVG_LOSS,MAX_LOSS"
wcursor.execute("""SELECT * from results_by_twp WHERE
     valid = '%s' ORDER by model_twp""" % (ts.strftime("%Y-%m-%d"),))
for row in wcursor:
    print ("%(valid)s,%(model_twp)s,%(min_runoff).4f,%(avg_runoff).4f,"
           "%(max_runoff).4f,%(min_loss).4f,%(avg_loss).4f,"
           "%(max_loss).4f") % row
