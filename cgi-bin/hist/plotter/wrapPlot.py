#!/usr/local/bin/python
# Script that is a wrapper to histPlot.csh
#  Actually a new concept
# Daryl Herzmann 30 Oct 2001

import cgi, os, random

tempFile = str( int( random.random() * 1000000000 ) )+".gif"

def Main():
	print 'Content-type: text/html \n\n'

	myForm = cgi.FormContent()
	try:
	  year	= str( int( myForm["year"][0] ) )
	  month = ("0"+str(int( myForm["month"][0] )))[-2:]
	  day	= ("0"+str(int( myForm["day"][0] )))[-2:]
	  hour	= ("0"+str(int( myForm["hour"][0] )))[-2:]
	  minute = ("0"+str(int( myForm["minute"][0] )))[-2:]
	except:
	  year = "2001"
	  month = "08"
	  day = "19"
	  hour = "17"
	  minute = "20"


	if ( year > 1 and year < 3000 ):
	  year = year		

	sysString = tempFile +" "+year+" "+month+" "+day+" "+hour+" "+minute
	print sysString

	os.system("/usr/local/mesonet/bin/createPlot.csh "+ sysString )

	if (not os.path.isfile("/home/httpd/html/tmp/"+ tempFile ) ):
		print "Something went horribly wrong..."

	print '<img src="/tmp/'+tempFile+'">'

Main()
