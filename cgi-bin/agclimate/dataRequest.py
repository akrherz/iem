#!/mesonet/python/bin/python
# This should handle all data requests
# 24 Jun 2002:	Get rid of front space on header...
#
#########################################################

import pg, cgi, regsub, re, style, sys

def addYear(statId):
	form = cgi.FormContent()
	year = str( form["year"][0] )
	return statId+"_"+year

def splitFields(sectText):
	return re.split(' ', sectText)[-1]

def printer(results, timeType):
	sep = " "
	for i in range(len(results)):
		thisRow = results[i][1:]
		for j in range(len(thisRow)):
			if (0 < j < 5 and timeType == "hourly") or ( 0 < j < 4 ):
				thisEntry = str(int(thisRow[j]))
			else:
				thisEntry = str(thisRow[j])
			print thisEntry+( 8 - len(thisEntry) ) * sep ,
		print 

def Main():
	form = cgi.FormContent()
	if not form.has_key("stations"):
		style.SendError("No station specified!")
	if not form.has_key("dataCols"):
		style.SendError("No data specified!")
	stations = form["stations"]
	dataCols = form["dataCols"]

	stationTables = map(addYear, stations)

	year = form["year"][0]
	startMonth = str( form["startMonth"][0] )
	startDay = str( form["startDay"][0] )
	endMonth = str( form["endMonth"][0] )
	endDay = str( form["endDay"][0] )
	timeType = form["timeType"][0]

	startTime = startMonth+"-"+startDay+"-"+year
	endTime = endMonth+"-"+endDay+"-"+year

	dataCols = tuple(dataCols)
	strDataCols =  str(dataCols)[1:-2]
        strDataCols = regsub.gsub("'", " ", strDataCols)


	if timeType == "hourly":
		mydb = pg.connect('campbellhourly', '10.10.10.10')
		strDataCols = "date_part('year', day) AS year, date_part('month', day) AS month, date_part('day', day) AS day, date_part('hour', day) AS hour, "+strDataCols
	else:
		mydb = pg.connect('campbelldaily', '10.10.10.10')
		strDataCols = "date_part('year', day) AS year, date_part('month', day) AS month, date_part('day', day) AS day, "+strDataCols


	print 'Content-type: text/plain \n\n'
	print """
# Output for Iowa State Ag Climate Station Data
# Notes on the format of this data and units can be found at
#	http://mesonet.agron.iastate.edu/agclimate/info.txt
# If you have trouble getting the data you want, please send email to akrherz@iastate.edu

"""


	for stationTable in stationTables:
		queryStr = "SELECT day as sortday, '"+stationTable[:-5]+"' as statid, "+strDataCols+" from "+stationTable+" WHERE day >= '"+startTime+"' and day <= '"+endTime+"' ORDER by sortday ASC"
	#	print queryStr
		try:
			results = mydb.query(queryStr)
		except:
			print "Error: Problem Querying Database.  Perhaps Incorrect date?"
			sys.exit(0)

		headings = results.listfields()[1:]
		strHeadings = str(tuple(headings))[1:-2]
	        strHeadings =  regsub.gsub("'", " ", strHeadings)
	        print  (regsub.gsub(",", " ", strHeadings))[1:]
		
		results = results.getresult()
		printer(results, timeType)

		print "\n\n\n"

	print "#EOF"

Main()
