#!/mesonet/python/bin/python
# This will be the master search engine into the Archived Iowa Weather Data
# Daryl Herzmann 3/30/99
# UPDATE 3/31/99: Working on download feature
# UPDATE 4/7/99: Adding in multi-station search
# 3 Mar 2004	Use site python

import style, functs, engine, sys
from cgi import *


def table_header():
        print '<TABLE WIDTH="600" BORDER="0" CELLSPACING="1" ROWSPACING="1">'
        print '<TR><TH><U>Station Code:</TH><TH><U>Date:</TH><TH><U>High Temp:</TH><TH><U>Low Temp:</TH><TH><U>Precip:</TH><TH><U>Snow:</U></TH></TR>'

def result_row(city, date, high, low, rain, snow):
	print '<TR><TD align="center">'+city+'</TD><TH>'+date+'</TH><TD align="center">'+high+'</TD><TD align="center">'+low+'</TD>'
	print '<TD align="center">'+rain+'</TD><TD align="center">'+snow+'</TD></TR>'

def table_footer():
	print '</TABLE>'

def convert_station(code):
        code = code[-4:]
        file = '/home/httpd/html/src/stations.con'
        f = open(file,'r').read()

        lines = re.split('\n',f)
        for i in range(len(lines)):
                line = lines[i]
                info = re.split(',',line)
                if code == info[0]:
                        name = info[3]
        return name


def Main():

	form = FormContent()

	query_option = form["query_option"][0]			# Determine which option is desired

	city = "None"			# Code for 
	city_name = "None"
	if form.has_key("city"):
		city = form["city"][0]
		city_name = functs.convert_station(city)

	year = "None"
	if form.has_key("year"):
		year = form["year"][0]

	month = "None"
	str_month = "None"
	if form.has_key("month"):
		month = form["month"][0]
		str_month = functs.convert_month("0"+month)

	day = "None"
	if form.has_key("day"):
		day = form["day"][0]

	if year == "none" or year == "None":
		style.SendError("You need to specify a search date.")

	style.header("Historical Iowa Weather Data Search Engine","white")	# Standard Setup HTML Document
	style.std_top("Query Results in Iowa Weather Data")			# Standard Header Information

	print '<TABLE NOBORDER>'
	print '<TR><TH colspan="4">Search Paramenters:</TH><TH colspan="6"><font color="red">Time Constraints:</red></TH></TR>'
	print '<TR><TH bgcolor="#EEEEE">Query Option:</TH><TD>'+query_option+'</TD>'
	print '<TH bgcolor="#EEEEE">Station Option:</TH><TD>'+city_name+'</TD>'
	print '<TH bgcolor="#EEEEE"><font color="red">Year:</font></TH><TD>'+year+'</TD>'
	print '<TH bgcolor="#EEEEE"><font color="red">Month:</font></TH><TD>'+str_month+'</TD>'
	print '<TH bgcolor="#EEEEE"><font color="red">Day:</font></TH><TD>'+day+'</TD>'
	print '</TR></TABLE>'

	if city == "None":
		print '<H2 align="center"><font color="blue"><U>Please Enter a city!!</U></font></H2>'
		style.std_bot()
		sys.exit()

	results = engine.search(query_option, city, year, month, day)

	print '<HR>'

	junk_string = 'query_option='+query_option+'&city='+city+'&year='+year+'&month='+month+'&day='+day
	print '<a href="download.py?'+junk_string+'"><B>Click to download this data set</B></a>'

	print '<HR>'

	if len(results) == 0:
		print '<P>This Query did not find any results in the Database system.<BR>'
		print '<P>Please review your query above and try again.<BR>'

	else:
		print '<H2 align="center"><font color="blue"><U>Weather Data for '+city_name+', Iowa</U></font></H2>'
		table_header()
		for i in range(len(results)):
			city = results[i][0]
	                day = results[i][1]
	                climoweek = results[i][2]
	                high  = results[i][3]
	                low = results[i][4]
	                rain = results[i][5]
	                snow = results[i][6]

			result_row(city, day, str(high), str(low), str(rain), str(snow) )
		table_footer()	

	style.std_bot()
Main()
