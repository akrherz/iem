#!/mesonet/python/bin/python
# 
# Rerun from historical snet data
# Daryl Herzmann 04 Mar 2002
#
##############################################################

import telnetlib, time, re, regsub, DateTime, math, os
from mesonet import *

logger = open('/tmp/nwn_rerun.log', 'w') 

def process(file):
  
	f = open(file, 'r').readlines()
	i = int( file[:-4] )
  
    # Loop over these lines
	for line in f:
		tokens = re.split(",",line)
		if (len(tokens) > 4):  # Simple test to make sure line is long
        # For now, we are ignoring the Max/Min lines
      
			myDate = tokens[1]
			myTime = tokens[0]
      
      
			thisTime = DateTime.strptime(myDate +" "+ myTime, "%m/%d/%y %H:%M")
      
			myMinute = int(myTime[3:5])
			if (myMinute == 0 or myMinute == 20 or myMinute == 40):
				gmtTime = thisTime + DateTime.RelativeDateTime(hours=+6)
				filePre = gmtTime.strftime("%Y%m%d")
				gempakTime = gmtTime.strftime("%y%m%d/%H%M")
				fref = open('/tmp/'+filePre+'.fil', 'a')
				try:
					fref.write("    "+ snetConv[i] +"    "+ gempakTime +"     ")
	
					tempF = int( (tokens[6])[:-1] )
					RH = int( (tokens[7])[:3] )
					dirTxt = tokens[2]
					mph = (tokens[3])[:-3]
					knots = round(float(mph) / 1.1507, 2)
					alti = tokens[8]
					p24i = (tokens[9])[:-2]
					srad = int( (tokens[4])[:-1] ) * 10

					drct = txt2drct[dirTxt]
					dwpf = dewPoint(float(tempF), float(RH) )

					fref.write( str(tempF) +"     "+ str(RH) +"   "+str(dwpf) +"      " \
				    + str(drct)+"     "+ str(knots) +"   "+ str(p24i) +"   "+ str(srad)+"\n")
				except KeyError:
					hi = "hello"

				fref.close()
	

def dewPoint(tmpf,relh):
  tmpk = 273.15 + ( 5.00/9.00 * ( tmpf - 32.00) )
  dwpk = tmpk / (1+ 0.000425 * tmpk * -(math.log10(relh/100.0)) )
 
  return int( ( dwpk - 273.15 ) * 9.00/5.00 + 32 )


def Main():

	files = os.listdir("/mesonet/ARCHIVE/raw/snet/2002_03/04/")
	os.chdir("/mesonet/ARCHIVE/raw/snet/2002_03/04/")
	for file in files:
		process( file )


Main()

