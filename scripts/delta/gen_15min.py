"""
 Name of the game, figure out 15 min deltas, dump to database
"""
import psycopg2.extras
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
import datetime

# First, we get a dict going of our current obs
icursor.execute("""SELECT *
	from current WHERE 
    (valid + '15 minutes'::interval) > CURRENT_TIMESTAMP and
    alti is not Null""")
c = {}
for row in icursor:
    sid = row["iemid"]
    c[sid] = {}
    c[sid] = row

# Now, we get obs from a 20 minute window, one hour ago
now = datetime.datetime.now()
w0 = now + datetime.timedelta(minutes=-20)
w1 = now + datetime.timedelta(minutes=-10)


sql = """SELECT c.*, s.id from current_log c, stations s
	WHERE s.iemid = c.iemid and
	valid BETWEEN '%s' and '%s' and alti is not null""" % (
	w0.strftime("%Y-%m-%d %H:%M"), w1.strftime("%Y-%m-%d %H:%M"))
icursor.execute(sql)
lh = {}
for row in icursor:
    sid = row["iemid"]
    lh[sid] = {}
    lh[sid] = row

# Now lets run through the obs
for sid in c.keys():
    if not lh.has_key(sid):
        continue
    d = c[sid]["alti"] - lh[sid]["alti"]
    if d == 0 and c[sid]['pres'] is not None and lh[sid]['pres'] is not None:
        d = c[sid]["pres"] - lh[sid]["pres"]
    #print id, c[id]["lat"], c[id]["lon"], c[id]["alti"], lh[id]["alti"], d
    if d < 1 and d > -1:
        icursor.execute("""UPDATE trend_15m t SET alti_15m = %s,
			updated = CURRENT_TIMESTAMP FROM stations s WHERE s.iemid = t.iemid 
			and s.id = '%s'
			""" % (d, lh[sid]['id']))

icursor.close()
IEM.commit()
