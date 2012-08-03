"""
 Name of the game, figure out 15 min deltas, dump to database
"""
import iemdb
import psycopg2.extras
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
import mx.DateTime

# First, we get a dict going of our current obs
icursor.execute("""SELECT *
	from current WHERE 
	(valid + '15 minutes'::interval) > CURRENT_TIMESTAMP and
    alti is not Null""")
c = {}
for row in icursor:
	id = row["iemid"]
	c[id] = {}
	c[id] = row

# Now, we get obs from a 20 minute window, one hour ago
now = mx.DateTime.now()
w0 = now + mx.DateTime.RelativeDateTime(minutes=-20)
w1 = now + mx.DateTime.RelativeDateTime(minutes=-10)


sql = """SELECT c.*, s.id from current_log c, stations s 
	WHERE s.iemid = c.iemid and 
	valid BETWEEN '%s' and '%s' and alti is not null""" % (
	w0.strftime("%Y-%m-%d %H:%M"), w1.strftime("%Y-%m-%d %H:%M") ) 
icursor.execute(sql)
lh = {}
for row in icursor:
	id = row["iemid"]
	lh[id] = {}
	lh[id] = row
	
# Now lets run through the obs
for id in c.keys():
	if not lh.has_key(id):
		continue
	d = c[id]["alti"] - lh[id]["alti"]
	if d == 0 and c[id]['pres'] is not None and lh[id]['pres'] is not None:
		d = c[id]["pres"] - lh[id]["pres"]
	#print id, c[id]["lat"], c[id]["lon"], c[id]["alti"], lh[id]["alti"], d
	if ( d < 1 and d > -1):
		icursor.execute("""UPDATE trend_15m t SET alti_15m = %s, 
		updated = CURRENT_TIMESTAMP FROM stations s WHERE s.iemid = t.iemid and s.id = '%s'
""" % (d, lh[id]['id']) )
		
icursor.close()
IEM.commit()

