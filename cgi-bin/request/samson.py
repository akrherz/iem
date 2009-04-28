#!/mesonet/python/bin/python
#		toSAMSON.py
# Test program to convert data into SAMSON format
# Daryl Herzmann 20 Aug 2001
# Lets make a bit more elegant and work for multiple stations

import pg, sys, re, cgi, string

mydb = pg.connect('asos','iemdb')
rwis = pg.connect('rwis')
ncdc = pg.connect('mesonet')


#print "~14933 DES MOINES             IA  -6  N41 32  W093 39   294"
#print "~YR MO DA HR I   12   13" 

def printHeader( stationID ):
	rs = ncdc.query("SELECT wban, name, lat, long, ground from ncdc WHERE call_sign = '"+ stationID +"' ").dictresult()
	try:	
		thisWBAN = rs[0]["wban"]
		thisName = rs[0]["name"][:-4]
	        thisState = rs[0]["name"][-2:]
	        thisLatInt = re.split('\.', rs[0]["lat"])[0]
	        thisLatSec = re.split('\.', rs[0]["lat"])[1]
	        thisLongInt = re.split('\.', rs[0]["long"])[0][1:]
	        thisLongSec = re.split('\.', rs[0]["long"])[1]
	except:
		rs = ncdc.query("SELECT name, state, lat, long from stations WHERE stationid = '"+ stationID +"' ").dictresult()

		thisWBAN = "99999"
		thisName = string.strip(rs[0]["name"])
		thisState = rs[0]["state"]
		thisLatInt = re.split('\.', rs[0]["lat"])[0]
		thisLatSec = re.split('\.', rs[0]["lat"])[1]
		thisLongInt = re.split('\.', rs[0]["long"])[0][1:]
		thisLongSec = re.split('\.', rs[0]["long"])[1]

#	print thisWBAN, thisName, thisState, thisLatInt, thisLatSec, thisLongInt, thisLongSec

	print "~"+ str(thisWBAN)+" "+ printCol( thisName, 22) +" "+ thisState +"  -6  N"+ str(thisLatInt) \
		+" "+ ("0"+thisLatSec)[-2:] +"  W"+ ("0"+thisLongInt)[-3:] +" "+ ("0"+thisLongSec)[-2:] +"   999"
	print "~YR MO DA HR I      8      9   12   13"

def colPrint(strTxt, colWidth):
	return " " * (colWidth - len(strTxt) ) + strTxt

def printCol(strTxt, colWidth):
	return strTxt + " " * (colWidth - len(strTxt) ) 


def Main():
	print 'Content-type: text/plain \n\n'
	form = cgi.FormContent()
	stationID = form["station"][0]
	printHeader( stationID )
	goodb = mydb
	if len(stationID) == 4:
		goodb = rwis

	rs = goodb.query("SELECT tmpf, dwpf, station, to_char(valid, 'yy mm dd HH24') as times , sknt / 2.00 as sknt, drct as int_drct \
        	from t2002 WHERE station = '"+ stationID +"' and drct > -1 and date_part('minute', valid) = 0 ORDER by valid").dictresult()


	for i in range(len( rs )):
		print " "+str( rs[i]["times"] ) + " 0 "\
			+ colPrint( str( rs[i]["tmpf"] ), 6) +" " \
			+ colPrint( str( rs[i]["dwpf"] ), 6) +" " \
			+ colPrint( str( int(rs[i]["int_drct"]) ), 4) +" " \
			+ colPrint( str( int(rs[i]["sknt"]) ), 4)
#
Main()
