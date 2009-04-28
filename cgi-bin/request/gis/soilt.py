#!/mesonet/python/bin/python
# Dump LSRs to a shapefile

import dbflib, mx.DateTime, zipfile, os, sys, shutil, cgi
from pyIEM import wellknowntext, iemdb

i = iemdb.iemdb()
mydb = i["isuag"]


# Get CGI vars
form = cgi.FormContent()
ts = mx.DateTime.strptime(form["ts"][0], "%Y%m%d")

os.chdir("/tmp/")
fp = "soilt_%s" % (ts.strftime("%Y%m%d%H%M"),  )

# Field 0: Type=String, Title=`SCODE', Width=20, Decimals=0
# Field 1: Type=Double, Title=`TODAY', Width=20, Decimals=5
dbf = dbflib.create(fp)
dbf.add_field("SCODE", dbflib.FTString, 20, 0)
dbf.add_field("TODAY", dbflib.FTDouble, 20, 5)


sql = "SELECT station, c30 from daily WHERE \
	valid = '%s' " % (ts.strftime("%Y-%m-%d"), )
rs = mydb.query(sql).dictresult()

cnt = 0
#print 'Content-type: text/plain\n\n'
for i in range(len(rs)):
	d = {}
	d["SCODE"] = rs[i]['station'].replace("A","")
	d["TODAY"] = float(rs[i]['c30'])
	dbf.write_record(i, d)


del(dbf)

print "Content-type: application/octet-stream"
print "Content-Disposition: attachment; filename=%s.dbf" % (fp,)
print

print file(fp+".dbf", 'r').read(),
