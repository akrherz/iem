#!/mesonet/python/bin/python
# Output by township

from pyIEM import iemdb, wellknowntext
import shapelib, dbflib, os, cgi, mx.DateTime, sys, zipfile, shutil
i = iemdb.iemdb()
mydb = i['wepp']


os.chdir('/tmp/')

# Figure out what date we want
form = cgi.FormContent()
year = int(form["year"][0])
month = int(form["month"][0])
day = int(form["day"][0])
ts = mx.DateTime.DateTime(year, month, day)
fp = "%s_sm" % (ts.strftime("%Y%m%d"), )
interval = None
if form.has_key("interval"):
    interval = int(form["interval"][0])
    fp = "%s_%s_sm" % (ts.strftime("%Y%m%d"), interval)

monthly = None
if form.has_key("monthly"):
    monthly = 1
    fp = "%s_sm" % (ts.strftime("%Y%m"), )


print "Content-type: application/octet-stream"
print "Content-Disposition: attachment; filename=%s.zip" % (fp,)
print

# Maybe our data is already cached, lets hope so!
if os.path.isfile(fp+".zip"):
  print file(fp+".zip", 'r').read(),
  sys.exit(0)


# Load up the township GIS stuff
twp = {}

sql = "SELECT astext(transform(the_geom,4326)) as tg, model_twp from iatwp"
if form.has_key("point"):
  sql = "SELECT astext(transform(centroid(the_geom),4326)) as tg, model_twp from iatwp"

rs = mydb.query(sql).dictresult()
for i in range(len(rs)):
  twp[ rs[i]["model_twp"] ] = rs[i]["tg"]

# Now, lets figure out what data we want
sql = "SELECT * from waterbalance_by_twp WHERE valid = '%s'" \
       % (ts.strftime("%Y-%m-%d"), )
day1 = ts.strftime("%Y%m%d")
day2 = ts.strftime("%Y%m%d")
if interval is not None:
    sql = "SELECT model_twp, avg(vsm) as vsm, -1 as vsm_stddev, \
      avg(s10cm) as s10cm, avg(s20cm) as s20cm from waterbalance_by_twp \
      WHERE valid BETWEEN '%s' and ('%s'::date + '%s days'::interval) \
      GROUP by model_twp" % (ts.strftime("%Y-%m-%d"), ts.strftime("%Y-%m-%d"),\
      interval)
    day2 = (ts + mx.DateTime.RelativeDateTime(days=interval)).strftime("%Y%m%d")

if monthly is not None:
    sql = "SELECT model_twp, avg(vsm) as vsm, -1 as vsm_stddev, \
      avg(s10cm) as s10cm, avg(s20cm) as s20cm from waterbalance_by_twp \
      WHERE valid BETWEEN '%s-01' and ('%s-01'::date + '1 month'::interval) \
      GROUP by model_twp" % (ts.strftime("%Y-%m"), ts.strftime("%Y-%m") )
    day1 = (ts + mx.DateTime.RelativeDateTime(day=1)).strftime("%Y%m%d")
    day2 = (ts + mx.DateTime.RelativeDateTime(day=1,months=1) - mx.DateTime.RelativeDateTime(days=1) ).strftime("%Y%m%d")

rs = mydb.query(sql).dictresult()

if form.has_key("point"):
  shp = shapelib.create(fp, shapelib.SHPT_POINT)
else:
  shp = shapelib.create(fp, shapelib.SHPT_POLYGON)
dbf = dbflib.create(fp)
dbf.add_field("DAY_STA", dbflib.FTString, 8, 0)
dbf.add_field("DAY_END", dbflib.FTString, 8, 0)
dbf.add_field("MODL_TWP", dbflib.FTString, 10, 0)
dbf.add_field("VSM", dbflib.FTDouble, 8, 4)
dbf.add_field("VSM_STDD", dbflib.FTDouble, 8, 4)
dbf.add_field("S10CM", dbflib.FTDouble, 8, 4)
dbf.add_field("S20CM", dbflib.FTDouble, 8, 4)

for i in range(len(rs)):
  m = rs[i]["model_twp"]
  vsm = float(rs[i]["vsm"])
  vsms = float(rs[i]["vsm_stddev"])
  s10 = float(rs[i]["s10cm"])
  s20 = float(rs[i]["s20cm"])

  f = wellknowntext.convert_well_known_text( twp[m] )
  if form.has_key("point"):
    obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, [[f]] )
  else:
    obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )
  shp.write_object(-1, obj)
  dbf.write_record(i, (day1,day2,m,vsm,vsms,s10,s20) )

del(dbf)
del(shp)

o = open(fp+".txt", 'w')
o.write("""
WEPP Modelled Soil Moisture from the Iowa Daily Erosion Project
http://wepp.mesonet.agron.iastate.edu

DBF Columns are:
  DAY_STA   Start date of the period data is valid for YYYYMMDD
  DAY_END   End date of the period data is valid for YYYYMMDD
  MODL_TWP  Model township
  VSM       Volumetric Soil Moisture [%] over root zone depth
  VSM_STDD  VSM Standard Deviation within model township
  S10CM     0-10 cm depth soil moisture [mm]
  S20CM     10-20 cm depth soil moisture [mm]

If DAY_STA does not equal DAY_END, then the values have been time 
averaged.  VSM_STDD is set to -1 in this case, since we don't have
necessary data to produce this statistic.

Data Contact:
  Daryl Herzmann akrherz@iastate.edu  515.294.5978

""")
o.close()

shutil.copyfile("/mesonet/data/gis/meta/4326.prj", fp+".prj")
z = zipfile.ZipFile(fp+".zip", 'w', zipfile.ZIP_DEFLATED)
z.write(fp+".shp")
z.write(fp+".shx")
z.write(fp+".dbf")
z.write(fp+".prj")
z.write(fp+".txt")
z.close()

print file(fp+".zip", 'r').read(),

os.remove(fp+".shp")
os.remove(fp+".shx")
os.remove(fp+".dbf")
os.remove(fp+".prj")
os.remove(fp+".txt")
