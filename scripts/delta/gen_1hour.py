# Name of the game, figure out 1 hour deltas, dump to netCDF

from pyIEM import iemAccessDatabase
import mx.DateTime
iemdb = iemAccessDatabase.iemAccessDatabase()

# First, we get a dict going of our current obs
rs = iemdb.query("SELECT *, x(geom) as lon, y(geom) as lat \
	from current WHERE \
	(valid + '1 hour'::interval) > CURRENT_TIMESTAMP").dictresult()
c = {}
for i in range(len(rs)):
	id = rs[i]["station"]
	c[id] = {}
	c[id] = rs[i]

# Now, we get obs from a 20 minute window, one hour ago
now = mx.DateTime.now()
lhour = now + mx.DateTime.RelativeDateTime(hours=-1, minute=0)
w0 = lhour + mx.DateTime.RelativeDateTime(hours=-1,minute=49)
w1 = lhour + mx.DateTime.RelativeDateTime(minute=11)


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

	if (d < 1 and d > -1):
		#print id, c[id]["lat"], c[id]["lon"], c[id]["alti"], lh[id]["alti"], d
		iemdb.query("UPDATE trend_1h SET alti_1h = %s, \
			updated = CURRENT_TIMESTAMP WHERE station = '%s'" % (d, id) )

