#!/mesonet/python/bin/python
# This program will request data from a station for a specified time
# Daryl Herzmann
# UPDATED 7-6-99: Changed which days get displayed
# 9-22-99: Checking up on code, clean up a bit
# 10-25-99: Added headers to the data that gets outputed

import cgi, time, re, pg, style

index_dict = { 'c100': 'Air T' , 'c11, c12' : 'High T \tLow T' , 'c90' : 'Precip' , 'c900' : 'Precip' , 'c300' : '4in So T', 'c30' : '4in So T', 'c70' : 'PET' , 'c80' : 'Solar Rad [Langleys]' , 'c800' : 'Solar Rad [Langleys]' }



def Main():
	form = cgi.FormContent()
	start_year = form["start_year"][0]
	end_year = form["end_year"][0]
	start_month = form["start_month"][0]
	end_month = form["end_month"][0]
	start_day = form["start_day"][0]
	end_day = form["end_day"][0]
	station = form["station"][0]
	db = form["db"][0]
	data_type = form["data_type"][0]

	mydb = pg.connect(db)

	data_type = re.split(',', data_type, 1)

	start_tuple = (int(start_year), int(start_month), int(start_day), 0, 0, 0, 0, 0, 0)
	end_tuple = (int(end_year), int(end_month), int(end_day), 0, 0, 0, 0, 0, 0)

	start_secs = time.mktime(start_tuple)
	end_secs = time.mktime(end_tuple)

	if start_secs > end_secs:
		style.SendError("Go back and check your dates.")

	days = int((end_secs - start_secs)/86400)

	final = []
	
	for day in range(0, days+1):
		this_sec = start_secs + (86400 * day)
		local = time.localtime(this_sec)
		year = time.strftime("%Y", local)
		month = time.strftime("%m", local)
		day = time.strftime("%d", local)
		sation = station+"_"+year
		if db == "campbell_hourly":
			select = mydb.query("SELECT yeer, month, day, tod, "+data_type[0]+" from "+sation+" WHERE (yeer = '"+year+"' AND month = '"+month+"' AND day = '"+day+"')")
		else:
			select = mydb.query("SELECT yeer, month, day, "+data_type[1]+" from "+sation+" WHERE (yeer = '"+year+"' AND month = '"+month+"' AND day = '"+day+"')")
		select = select.getresult()
		final = final + select



	print 'Content-type: text/html \n\n'
	print '<PRE>'
	if db == "campbell_hourly":
		print 'Station Year \tMonth \tDay \tHour\t'+index_dict[data_type[1]]+'\n'
	else:
		print 'Station Year \tMonth \tDay \t'+index_dict[data_type[1]]+'\n'
	select = final
#	select.sort()
	for i in range(len(select)):
		print station[3:8]+"\t",
		for j in range(len(select[i])):
			print select[i][j],"\t",
		print 

	print '</PRE>'


Main()
