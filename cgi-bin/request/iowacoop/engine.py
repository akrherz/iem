#!/mesonet/python/bin/python
# This file is the one that runs the search engine for the various files
# Daryl Herzmann 3/31/99
# UPDATE: 4/7/99 - Adding in allstations search
# 28 Aug 2002: coop db is on db1.mesonet
# 19 May 2003	Use the all data table

import functs, pg


mydb = pg.connect('coop', 'db1.mesonet', 5432)

def search(option, city, year, month, day):
	
	results = []
	dateStr = year+"-"+month+"-"+day

	if option == "yearly":

		print '<BR><a href="year_graph.py?city='+city+'&year='+year+'">Click Here for a graph of this data</a><BR>'

		results = mydb.query("SELECT * from alldata WHERE stationid = '"+city+"' and day >= "+year+" and day <= '"+year+"-12-31' ORDER by day  ")
		results = results.getresult()

	if option == "monthly":
		results = mydb.query("SELECT * from alldata WHERE stationid = '"+city+"' and day >= '"+year+"-"+month+"-01' ORDER by day LIMIT 31 ")
		results = results.getresult()

	if option == "daily":
		results = mydb.query("SELECT * from alldata WHERE stationid = '"+city+"' and day = '"+dateStr+"'")
		results = results.getresult()

	if option == "allstations_daily":
		stations = functs.stations()
#		for i in range(len(stations)):
		for i in range(10):
			code = stations[i][1]
			tmp_results = mydb.query("SELECT * from "+code+" WHERE day = '"+dateStr+"'")
			tmp_results = tmp_results.getresult()
			results = results + tmp_results

	return results
