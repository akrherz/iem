# Name of the game, figure out 1 hour deltas, dump to netCDF

import iemdb
import psycopg2.extras
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
import mx.DateTime

# First, we get a dict going of our current obs
icursor.execute("""SELECT s.id as station, c.*, x(s.geom) as lon, 
 y(s.geom) as lat  from current c, stations s WHERE 
 (valid + '1 hour'::interval) > CURRENT_TIMESTAMP and 
 alti is not Null and c.iemid = s.iemid""")
c = {}
for row in icursor:
	id = row["station"]
	c[id] = {}
	c[id] = row

# Now, we get obs from a 20 minute window, one hour ago
now = mx.DateTime.now()
lhour = now + mx.DateTime.RelativeDateTime(hours=-1, minute=0)
w0 = lhour + mx.DateTime.RelativeDateTime(hours=-1,minute=49)
w1 = lhour + mx.DateTime.RelativeDateTime(minute=11)


sql = """SELECT c.*, t.id from current_log c, stations t WHERE 
	t.iemid = c.iemid and valid BETWEEN '%s' and '%s' and 
	alti is not null""" % (w0.strftime("%Y-%m-%d %H:%M"), 
	w1.strftime("%Y-%m-%d %H:%M") ) 
icursor.execute( sql )
lh = {}
for row in icursor:
	id = row["id"]
	lh[id] = {}
	lh[id] = row

# Now lets run through the obs
for id in c.keys():
	if (not lh.has_key(id)): continue
	d = c[id]["alti"] - lh[id]["alti"]
	if d == 0 and c[id]['pres'] is not None and lh[id]['pres'] is not None:
		d = c[id]["pres"] - lh[id]["pres"]

	if (d < 1 and d > -1):
		#print id, c[id]["lat"], c[id]["lon"], c[id]["alti"], lh[id]["alti"], d
		icursor.execute("""UPDATE trend_1h t SET alti_1h = %s, 
			updated = CURRENT_TIMESTAMP FROM stations s 
   WHERE s.iemid = t.iemid and s.id = '%s'""" % (d, id) )

IEM.commit()
