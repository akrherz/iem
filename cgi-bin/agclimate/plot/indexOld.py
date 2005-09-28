#!/usr/local/bin/python
# This is the file that will plot anything asked for
# Daryl Herzmann 7-11-99
# 9-10-99: Fixed a strange problem with the precip

import DateTime, time, cgi, style, plot, regsub
# from pgext import *

def decide_time(form):
	if form.has_key("yeer"):
		yeer = form["yeer"][0]
		month = form["month"][0]
		day = form["day"][0]
		time_tuple = (int(yeer), int(month), int(day),  12, 36, 20, 4, 127, 1)
		secs = time.mktime(time_tuple)
		return time.time()-86400 . secs
	elif form.has_key("secs"):
		secs = form["secs"][0]
		return time.time()-86400 , secs
	else:
		return time.time()-86300 , time.time()-86400

def data_options(data, secs):
	print '<form method="POST" name="mode" action="index.py">'
	print '<INPUT TYPE="hidden" name="secs" value="'+str(secs)+'">'
	print '<SELECT name="data" onChange="location=this.form.data.options[this.form.data.selectedIndex].value">'

	print '<option value="index.py?data=c40&secs='+str(secs)+'" '
	if data == "c40": print "SELECTED"
	print '>Average Wind Speed'

	print '<option value="index.py?data=c529,_c530&secs='+str(secs)+'" '
	if data == "c529, c530": print "SELECTED"
	print '>Five Sec Wind Gust'

	print '<option value="index.py?data=c11,_c12&secs='+str(secs)+'" '
	if data == "c11, c12": print "SELECTED"
	print '>High and Low Temps'

	print '<option value="index.py?data=c70&secs='+str(secs)+'" '
	if data == "c70": print "SELECTED"
	print '>Potential ET'

	print '<option value="index.py?data=c90&secs='+str(secs)+'" '
	if data == "c90": print "SELECTED"
	print '>Precipitation'

	print '<option value="index.py?data=c30&secs='+str(secs)+'" '
	if data == "c30": print "SELECTED"
	print '>Four Inch Soil Temperatures'

	print '<option value="index.py?data=c300&secs='+str(secs)+'" '
	if data == "c300": print "SELECTED"
	print '>Max/Min 4 in Soil Temperatures'

	print '<option value="index.py?data=c80&secs='+str(secs)+'" '
	if data == "c80": print "SELECTED"
	print '>Total Solar Radiation'

	print '<option value="index.py?data=c1&secs='+str(secs)+'" '
	if data == "c1": print "SELECTED"
	print '>Max/Min Dew Points'

	print '</SELECT>'
	print '</form>'

def prev_month(data, req_time):
	last_time = req_time + DateTime.RelativeDateTime(months=-1)
	secs = last_time.ticks()
	print '<form method="POST" name="last_month" action="index.py">'
	print '<input type="hidden" name="data" value="'+data+'">'
	print '<input type="hidden" name="secs" value="'+str(secs)+'">'
	print '<input type="image" src="/icons/camp_prev_month.jpg" BORDER="0">'
	print '</form>'

def next_month(data, req_time):
	last_time = req_time + DateTime.RelativeDateTime(months=+1)
	secs = last_time.ticks()
	print '<form method="POST" name="next_month" action="index.py">'
	print '<input type="hidden" name="data" value="'+data+'">'
	print '<input type="hidden" name="secs" value="'+str(secs)+'">'
	print '<input type="image" src="/icons/camp_next_month.jpg" BORDER="0">'
	print '</form>'

def next_day(data, req_time):
	last_time = req_time + DateTime.RelativeDateTime(days=+1)
	secs = last_time.ticks()
	print '<form method="POST" name="next_day" action="index.py">'
	print '<input type="hidden" name="data" value="'+data+'">'
	print '<input type="hidden" name="secs" value="'+str(secs)+'">'
	print '<input type="image" src="/icons/camp_next_day.jpg" BORDER="0">'
	print '</form>'

def prev_day(data, req_time):
	last_time = req_time + DateTime.RelativeDateTime(days=-1)
	secs = last_time.ticks()
	print '<form method="POST" name="prev_day" action="index.py">'
	print '<input type="hidden" name="data" value="'+data+'">'
	print '<input type="hidden" name="secs" value="'+str(secs)+'">'
	print '<input type="image" src="/icons/camp_prev_day.jpg" BORDER="0">'
	print '</form>'

def next_year(data, req_time):
	last_time = req_time + DateTime.RelativeDateTime(years=+1)
	secs = last_time.ticks()
	print '<form method="POST" name="next_year" action="index.py">'
	print '<input type="hidden" name="data" value="'+data+'">'
	print '<input type="hidden" name="secs" value="'+str(secs)+'">'
	print '<input type="image" src="/icons/camp_next_year.jpg" BORDER="0">'
	print '</form>'

def prev_year(data, req_time):
	last_time = req_time + DateTime.RelativeDateTime(years=-1)
	secs = last_time.ticks()
	print '<form method="POST" name="prev_year" action="index.py">'
	print '<input type="hidden" name="data" value="'+data+'">'
	print '<input type="hidden" name="secs" value="'+str(secs)+'">'
	print '<input type="image" src="/icons/camp_prev_year.jpg" BORDER="0">'
	print '</form>'

def print_date(secs):
	time_tuple = time.localtime(secs)
	nice_date = time.strftime("%B %d, %Y", time_tuple)
	print nice_date

def Main():
	form = cgi.FormContent()
	now, secs = decide_time(form)	# Figure out the time wanted by the form values
	data = "c11, c12" 	# Default to temperature maps
	if form.has_key("data"):
		data = form["data"][0]	
		data = regsub.gsub('_',' ', data)

	req_time = DateTime.localtime(secs)	# Convert this into a DateTime format

	style.header("ISU Agclimate Data Plotter","white")	# Setup HTML

	print '<TABLE width="100%">'

	print '<TR><TH bgcolor="red"><font color="white">Select Data Type:</TH>'
	print '<TH colspan="6" bgcolor="blue"><font color="white">Navigation:</TH>'
	print '</TR>'

	print '<TR><TD>'
	data_options(data, secs)

	print '</TD><TD>'
	prev_year(data, req_time)
	print '</TD><TD>'
	prev_month(data, req_time)
	print '</TD><TD>'
	prev_day(data, req_time)
	print '</TD><TD>'
	next_day(data, req_time)
	print '</TD><TD>'
	next_month(data, req_time)
	print '</TD><TD>'
	next_year(data, req_time)
	print '</TD></TR>'
	print '</TABLE>'

	if float(now) < float(secs) :
		print '<H1>You expect me to plot into the future?  I am good, but not that good :)</H1>'
	else:
		plot.plot(data, secs)
	
	print '<BR><BR><a href="/agclimate/index.html">ISU Agclimate Homepage</a>'

Main()
