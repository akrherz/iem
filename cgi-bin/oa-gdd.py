#!/mesonet/python/bin/python

# Produce a OA GDD Plot, dynamically!
import sys, os
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
os.environ[ 'HOME' ] = '/tmp/'
os.environ[ 'USER' ] = 'nobody'
import iemplot
import cgi
import datetime
import network

from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']
mesosite = i['mesosite']

form = cgi.FieldStorage()
if ("year1" in form and "year2" in form and 
    "month1" in form and "month2" in form and
    "day1" in form and "day2" in form):
    sts = datetime.datetime(int(form["year1"].value), 
      int(form["month1"].value), int(form["day1"].value))
    ets = datetime.datetime(int(form["year2"].value), 
      int(form["month2"].value), int(form["day2"].value))
else:
    sts = datetime.datetime(2011,5,1)
    ets = datetime.datetime(2011,10,1)
baseV = 50
if "base" in form:
    baseV = int(form["base"])
maxV = 86
if "max" in form:
    maxV = int(form["max"])


# Make sure we aren't in the future
now = datetime.datetime.today() 
if ets > now:
    ets = now

st = network.Table("IACLIMATE")
# Now we load climatology
#sts = {}
#rs = mesosite.query("SELECT id, x(geom) as lon, y(geom) as lat from stations WHERE \
#    network = 'IACLIMATE'").dictresult()
#for i in range(len(rs)):
#    sts[ rs[i]["id"].lower() ] = rs[i]


# Compute normal from the climate database
sql = """SELECT stationid,
   sum(gddXX(%s, %s, high, low)) as gdd
   from alldata WHERE year = %s and day >= '%s' and day < '%s'
   GROUP by stationid""" % (baseV, maxV, sts.year, sts.strftime("%Y-%m-%d"),
                            ets.strftime("%Y-%m-%d"))

lats = []
lons = []
gdd50 = []
valmask = []
rs = coop.query(sql).dictresult()
for i in range(len(rs)):
  id = rs[i]['stationid'].upper()
  if not st.sts.has_key(id):
    continue
  lats.append( st.sts[id]['lat'] )
  lons.append( st.sts[id]['lon'] )
  gdd50.append( rs[i]['gdd'] )
  valmask.append( True )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 '_showvalues'        : True,
 '_valueMask'         : valmask,
 '_format'            : '%.0f',
 '_title'             : "Iowa %s thru %s GDD(base=%s,max=%s) Accumulation" % (
                        sts.strftime("%Y: %d %B"), (ets - datetime.timedelta(days=1)).strftime("%d %B"),
                        baseV, maxV),
 'lbTitleString'      : "F",
}
# Generates tmp.ps
tmpfp = iemplot.simple_contour(lons, lats, gdd50, cfg)
iemplot.webprocess(tmpfp)
