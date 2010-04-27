#!/mesonet/python/bin/python
# Script to take current obs and make a SHEF file out of them...
# Daryl Herzmann 18 Feb 2002
# 20 Feb 2002:	Getting closer, now know what filename should be
# 27 Feb 2002:	If TA is too large, ignore ob
#		Time to send down to the NWS...
# 11 Nov 2002:	Use mx.DateTime now

import os, re, mx.DateTime
from mesonet import *

now = mx.DateTime.now()
lDate = now.strftime("%m/%d/%y")
sDate = now.strftime("%m%d")
hour = now.strftime("%H")

out = open('SUADSMRR5DSM.dat','w')

def writeHeader():
	out.write(".B DMX "+sDate+" CS DH"+str(hour)+"/TA/PPH\n")
	out.write(":Location ID   Prec Accum\n")
	out.write(":IEM\n")


def Main():
	writeHeader()
	files = os.listdir("../current/")
	for file in files:
		sid = file[0:4]
		if (sid == "SHUL"):
			continue
		idnum = snetConvBack[sid]
		f = open("../current/"+file, 'r').readlines()
		tokens = re.split(",", f[0])
	#	print "--------------------"
	#	print tokens
		strDate = tokens[1]
		strTime = tokens[0]
		thisTime = mx.DateTime.strptime(strDate +" "+ strTime , "%m/%d/%y %H:%M")
		topHour = thisTime + mx.DateTime.RelativeDateTime(hours=-1, minute=0)
		
		fileRef = topHour.strftime("/mesonet/ARCHIVE/raw/snet/%Y_%m/%d/"+str(idnum)+".dat")
		lookingTime = int( topHour.strftime("%H%M") )
		lines = open(fileRef, 'r').readlines()
		
		lastPrecip = -99
		
		for line in lines:
			parts = re.split(",", line)
			try:
				thisT = int( str(parts[0][:-3]) + str(parts[0][-2:]) )
			except:
				continue
			if (thisT > (lookingTime -5 ) and thisT < (lookingTime + 5)):
				lastPrecip = float(parts[10][:-2])
	#			print lastPrecip
	#			print parts
				break
			
		PP = float(tokens[10][:-2])
		if (lastPrecip == -99):
			PPH = 0.00
		else:
			PPH = round(PP - lastPrecip, 2 )
		TA = int(tokens[6][:-1])
	#	print TA, PPH, strDate, lDate
		
		if (PPH < 0):
	#		print TA, PPH, strDate, lDate
			PPH = 0.00
			
		if (TA > 200):
			continue
		
		if (strDate == lDate):
			out.write(sid +"      "+ str(TA) +" / "+ str(PPH) +"\n")
			


Main()
out.write(".END\n")
out.close()
