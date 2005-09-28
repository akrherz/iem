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
rs = mydb.query("SELECT tmpf::int as tmpf, dwpf::int as dwpf , station, to_char(valid, 'yymmddHH24MI') as times , sknt::int as sknt, drct::int as drct   from t2001 WHERE station = '"+ thisStation +"' ").dictresult()

print "Station	Valid(GMT)	TMPF	DWPF	SKNT	DRCT"

for i in range(len( rs )):
#	print rs[i]
#	print rs[i]["station"] +"  " \

	print str(thisStation) \
		+ "\t"+ str( rs[i]["times"] ) \
		+ "\t"+str( rs[i]["tmpf"] ) \
		+ "\t"+str( rs[i]["dwpf"] ) \
		+ "\t"+str( rs[i]["sknt"] ) \
		+ "\t"+str( rs[i]["drct"] ) 
