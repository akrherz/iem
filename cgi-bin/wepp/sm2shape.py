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

print "Content-type: application/octet-stream"
print "Content-Disposition: attachment; filename=%s.zip" % (fp,)
print

if (os.path.isfile(fp+".zip")):
  print file(fp+".zip", 'r').read(),
  sys.exit(0)


twp = {}
rs = mydb.query("SELECT astext(transform(the_geom,4326)) as tg, model_twp from iatwp").dictresult()
for i in range(len(rs)):
  twp[ rs[i]["model_twp"] ] = rs[i]["tg"]

rs = mydb.query("SELECT * from waterbalance_by_twp \
  WHERE valid = '%s'" % (ts.strftime("%Y-%m-%d"), ) ).dictresult()

shp = shapelib.create(fp, shapelib.SHPT_POLYGON)
dbf = dbflib.create(fp)
dbf.add_field("VALID", dbflib.FTString, 8, 0)
dbf.add_field("MODL_TWP", dbflib.FTString, 10, 0)
dbf.add_field("VSM", dbflib.FTDouble, 8, 4)
dbf.add_field("VSM_STDD", dbflib.FTDouble, 8, 4)
dbf.add_field("S10CM", dbflib.FTDouble, 8, 4)
dbf.add_field("S20CM", dbflib.FTDouble, 8, 4)

v = ts.strftime("%Y%m%d")
for i in range(len(rs)):
  m = rs[i]["model_twp"]
  vsm = float(rs[i]["vsm"])
  vsms = float(rs[i]["vsm_stddev"])
  s10 = float(rs[i]["s10cm"])
  s20 = float(rs[i]["s20cm"])

  f = wellknowntext.convert_well_known_text( twp[m] )
  obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )
  shp.write_object(-1, obj)
  dbf.write_record(i, (v,m,vsm,vsms,s10,s20) )

del(dbf)
del(shp)

o = open(fp+".txt", 'w')
o.write("""
IEM Modelled Soil Moisture from the Iowa Daily Erosion Project
http://wepp.mesonet.agron.iastate.edu

DBF Columns are:
  MODL_TWP  Model township
  VALID     Date data is valid for YYYYMMDD
  VSM       Volumetric Soil Moisture [%]
  VSM_STDD  VSM Standard Deviation within model township
  S10CM     0-10 cm depth soil moisture [mm]
  S20CM     10-20 cm depth soil moisture [mm]

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
