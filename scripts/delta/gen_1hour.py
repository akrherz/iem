""" Name of the game, figure out 1 hour deltas, dump to netCDF"""
import psycopg2.extras
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
import mx.DateTime

# First, we get a dict going of our current obs
icursor.execute("""SELECT s.id as station, c.*, ST_x(s.geom) as lon,
     ST_y(s.geom) as lat  from current c, stations s WHERE
     (valid + '1 hour'::interval) > CURRENT_TIMESTAMP and
     alti is not Null and c.iemid = s.iemid""")
c = {}
for row in icursor:
    sid = row["station"]
    c[sid] = {}
    c[sid] = row

# Now, we get obs from a 20 minute window, one hour ago
now = mx.DateTime.now()
lhour = now + mx.DateTime.RelativeDateTime(hours=-1, minute=0)
w0 = lhour + mx.DateTime.RelativeDateTime(hours=-1, minute=49)
w1 = lhour + mx.DateTime.RelativeDateTime(minute=11)


sql = """SELECT c.*, t.id from current_log c, stations t WHERE
    t.iemid = c.iemid and valid BETWEEN '%s' and '%s' and
    alti is not null
    """ % (w0.strftime("%Y-%m-%d %H:%M"), w1.strftime("%Y-%m-%d %H:%M"))
icursor.execute(sql)
lh = {}
for row in icursor:
    sid = row["id"]
    lh[sid] = {}
    lh[sid] = row

# Now lets run through the obs
for sid in c.keys():
    if sid not in lh:
        continue
    d = c[sid]["alti"] - lh[sid]["alti"]
    if d == 0 and c[sid]['pres'] is not None and lh[sid]['pres'] is not None:
        d = c[sid]["pres"] - lh[sid]["pres"]

    if (d < 1 and d > -1):
        icursor.execute("""UPDATE trend_1h t SET alti_1h = %s,
            updated = CURRENT_TIMESTAMP FROM stations s
   WHERE s.iemid = t.iemid and s.id = '%s'""" % (d, sid))

IEM.commit()
