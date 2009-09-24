# Name of the game, figure out 15 min deltas, dump to netCDF

from pyIEM import iemAccess, iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()
import mx.DateTime

# First, we get a dict going of our current obs
rs = iemdb.query("SELECT *, x(geom) as lon, y(geom) as lat \
	from current WHERE \
	(valid + '15 minutes'::interval) > CURRENT_TIMESTAMP").dictresult()
c = {}
for i in range(len(rs)):
	id = rs[i]["station"]
	c[id] = {}
	c[id] = rs[i]

# Now, we get obs from a 20 minute window, one hour ago
now = mx.DateTime.now()
w0 = now + mx.DateTime.RelativeDateTime(minutes=-20)
w1 = now + mx.DateTime.RelativeDateTime(minutes=-10)


sql = "SELECT * from current_log WHERE \
	valid BETWEEN '%s' and '%s'" % (w0.strftime("%Y-%m-%d %H:%M"), \
	w1.strftime("%Y-%m-%d %H:%M") ) 
rs = iemdb.query(sql).dictresult()
lh = {}
for i in range(len(rs)):
	id = rs[i]["station"]
	lh[id] = {}
	lh[id] = rs[i]
# Now lets run through the obs
for id in c.keys():
	if (not lh.has_key(id)): continue
	d = c[id]["alti"] - lh[id]["alti"]
	if (d == 0):
		d = c[id]["pres"] - lh[id]["pres"]
	#print id, c[id]["lat"], c[id]["lon"], c[id]["alti"], lh[id]["alti"], d
	if ( d < 1 and d > -1):
		iemdb.query("UPDATE trend_15m SET alti_15m = %s, \
			updated = CURRENT_TIMESTAMP WHERE station = '%s'" % (d, id) )

