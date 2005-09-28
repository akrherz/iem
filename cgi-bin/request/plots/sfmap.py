#!/usr/bin/python
# Script to allow dynamic creation of plotting scripts
# Daryl Herzmann 26 Feb 2002

import cgi, DateTime, random, os


def Main():
	print 'Content-type: text/html\n\n'

	form = cgi.FormContent()
	year= form["year"][0]
	month = form["month"][0]
	day = form["day"][0]
	hour = form["hour"][0]

	if len(str(year)) > 2:
		datefmt = "%Y %m %d %H"
	else:
		datefmt = "%y %m %d %H"
	datestr = str(year) +" "+ str(month) +" "+ str(day) +" "+ str(hour)
	myTime = DateTime.strptime( datestr, datefmt) 

	asosFile = "/mesonet/ARCHIVE/gempak/surface/ASOS/"+ \
		myTime.strftime("%Y_%m/%y%m%d_asos.gem")
	awosFile = "/mesonet/ARCHIVE/gempak/surface/AWOS/"+ \
		myTime.strftime("%Y_%m/%y%m%d_awos.gem")
	rwisFile = "/mesonet/ARCHIVE/gempak/surface/RWIS/"+ \
		myTime.strftime("%Y_%m/%y%m%d_rwis.gem")
	
	gdattim = myTime.strftime("%y%m%d/%H00")

	tmpfile = random.random()
	
	try:	
		os.mkdir("/tmp/gempakweb/")
	except:
		hi = "hello"
	os.chdir("/tmp/gempakweb/")
	o = open(str(tmpfile), 'w')
	
	o.write("#!/bin/csh\n\n")
	
	o.write("source /home/nawips/Gemenviron\n")
	o.write("cp /mesonet/restore/coltbl.xwp .\n")
	o.write("setenv DISPLAY localhost:1\n\n")
	
	o.write("sfmap << EOF > "+str(tmpfile)+".log\n")
	o.write(" restore /mesonet/restore/dewpts\n")
	o.write(" DEVICE = GF|"+str(tmpfile)+".gif\n")
	o.write(" SFFILE = "+asosFile+"\n")
	o.write(" DATTIM = "+gdattim+"\n")
	o.write(" TITLE  = 0\n")
	o.write(" COLORS = 4\n")
	o.write(" list\n")
	o.write(" run\n\n\n")
	
	o.write(" SFFILE = "+awosFile+"\n")
	o.write(" COLORS = 2\n")
	o.write(" TITLE  = 0\n")
	o.write(" list\n")
	o.write(" run\n\n\n")
	
	o.write(" SFFILE = "+rwisFile+"\n")
	o.write(" COLORS = 8\n")
	o.write(" TITLE  = 32/-1/~ dwpf ASOS[blue] AWOS[red] RWIS[brown]\n")
	o.write(" list\n")
	o.write(" run\n\n\n")
	
	o.write("EOF\n")
	o.write("\ngpend\n")
	
	o.write("if (-e "+str(tmpfile) +") then\n")
	o.write("  mv "+str(tmpfile)+".gif /mesonet/www/html/tmp/\n")
	o.write("endif\n")
	
	o.close()
	
	os.system("chmod +x "+str(tmpfile) )
	
	
	os.system("./"+str(tmpfile) )

	print "<img src=\"/tmp/"+str(tmpfile)+".gif\">\n"
	
	print "<p>Done:\n"
Main()
