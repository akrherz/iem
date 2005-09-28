#!/usr/bin/python

import pg, cgi

asosdb = pg.connect('asos','10.10.10.20')
rwisdb = pg.connect('rwis')
mydb2 = pg.connect('mesonet')

form = cgi.FormContent()
thisStation = form["station"][0]

print 'Content-type: text/plain \n\n'

mydb = asosdb
if len(thisStation) == 4:
	mydb = rwisdb


mydb.query(" SET TIME ZONE 'GMT' ")
rs = mydb.query("SELECT tmpf::int as tmpf , station, to_char(valid, 'yymmddHH24') as times , sknt, (drct / 10)::int as int_drct  from t2001 WHERE station = '"+ thisStation +"' and date_part('minute', valid) = 0 ").dictresult()

rs2 = mydb2.query("SELECT wban from ncdc WHERE call_sign = '"+ thisStation +"' ").dictresult()
try:	
	thisCode = rs2[0]["wban"]
except:
	print "The WBAN number can not be found for this station!  Using 99999\n"
	thisCode = "99999"

for i in range(len( rs )):
#	print rs[i]
#	print rs[i]["station"] +"  " \

	print str(thisCode) \
		+ str( rs[i]["times"] ) \
		+ "000" \
		+ ("0"+str( int(rs[i]["int_drct"]) ))[-2:] \
		+ ("00"+str( int(rs[i]["sknt"]) ))[-3:] \
		+ ("00"+str( int( rs[i]["tmpf"]) ))[-3:] \
		+"0000"
