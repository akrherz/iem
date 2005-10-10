#!/mesonet/python/bin/python
# This is the main page for the Iowa archive weather data
# Daryl Herzmann 1/14/99
# UPDATED: 4/7/99: Time to add multi-station features
# 28 Aug 2002:	coop db is on db1.mesonet
# 3 Mar 2004	updates!

import os, functs
from pyIEM import style, std_table, calendar
from cgi import *


stations = functs.stations()

def html_setup():
	style.header("Historical Iowa Weather Data","white")
	print """
<div style="text-align: center; margin: 10px; font-size: larger; background: #eee; border: 1px dashed #000;">While this
interface still works, you may wish to use the <a href='/request/coop/fe.phtml'>new and improved one</a>.</div>"""
	print '<table>'
	std_table.side_setup()

	options = [('Daily','index.py?opt=daily'),('Monthly','index.py?opt=monthly'),('Yearly','index.py?opt=yearly')]
	std_table.side_content("One Station Search Options:", options)

#	options = [('Yearly','index.py?opt=graph_yearly'),('Multi-Year','index.py?opt=graph_multiyear')]
	options = [('Yearly','index.py?opt=graph_yearly')]
	std_table.side_content("Graphing Options:", options)

	std_table.side_end()
	
def make_daily():
	print '<form method="POST" action="search.py">'
	print '<input type="hidden" name="query_option" value="daily">'
	print '<td>'
	print '<CENTER><H2>Search Archive by Date</H2>'
	print '<TABLE>'

	functs.form_years()

	functs.form_months()
	
	functs.form_days()

	functs.form_stations()

	functs.form_submit()	

	print '</table></td>'

def make_graph_yearly():
	print '<form method="POST" action="year_graph.py">'
	print '<input type="hidden" name="query_option" value="yearly">'
	print '<td>'
	print '<CENTER><H2>Graph yearly data for:</H2>'
	print '<TABLE>'

	functs.form_years()

	functs.form_stations()

	functs.form_submit()	

	print '</table></td>'

def make_monthly():
	print '<form method="POST" action="search.py">'
	print '<input type="hidden" name="query_option" value="monthly">'
	print '<td>'
	print '<CENTER><H2>Search Archive by Month</H2>'
	print '<TABLE><TR><TH>Enter a Year between 1893 - 1 Feb 2004:</TH>'
	print '<td><input type="text" size="4" name="year"></td></tr>'
	print '<TR><TH>Select a month:</TH>'
	print '<td><SELECT name="month">'
	months = ('January','February','March','April','May','June','July','August','September','October','November','December')
	for i in range(12):
		j = str(i+1)
		print '<option value="'+j+'">'+months[i]
	print '</SELECT></td></tr>'
	print '<tr><th>Select a Station:</th>'
	print '<td><SELECT name="city" size="6">'
	for i in range(len(stations)):
		print '<option value="'+stations[i][1]+'">'+stations[i][0]
	print '</SELECT></td></tr>'

	print '<tr><th>Submit Search:</th>'
	print '<td><input type="submit"></td></tr>'
	print '</table></td>'

def make_yearly():
	print '<form method="POST" action="search.py">'
	print '<input type="hidden" name="query_option" value="yearly">'
	print '<td>'
	print '<CENTER><H2>Search Archive by Year</H2>'
	print '<TABLE><TR><TH>Enter a Year between 1893 - 1 Feb 2004:</TH>'
	print '<td><input type="text" size="4" name="year"></td></tr>'
	print '</SELECT></td></tr>'
	print '<tr><th>Select a Station:</th>'
	print '<td><SELECT name="city" size="6">'
	for i in range(len(stations)):
		print '<option value="'+stations[i][1]+'">'+stations[i][0]
	print '</SELECT></td></tr>'

	print '<tr><th>Submit Search:</th>'
	print '<td><input type="submit"></td></tr>'
	print '</table></td>'

def make_allstations_daily():
	print '<input type="hidden" name="query_option" value="allstations_daily">'
	print '<td>'
	print '<CENTER><H2>Search Archive by Date for all stations:</H2>'
	print '<TABLE><TR><TH>Enter a Year between 1893 - 1 Feb 2004:</TH>'
	print '<td><input type="text" size="4" name="year"></td></tr>'
	print '<TR><TH>Select a month:</TH>'
	print '<td><SELECT name="month">'
	months = ('January','February','March','April','May','June','July','August','September','October','November','December')
	for i in range(12):
		j = str(i+1)
		print '<option value="'+j+'">'+months[i]
	print '</SELECT></td></tr>'
	print '<tr><th>Select a day:</th>'
	print '<td><SELECT name="day">'
	for i in range(31):
		i = str(i+1)
		print '<option value="'+i+'">'+i
	print '</SELECT></td></tr>'

	print '<tr><th>Submit Search:</th>'
	print '<td><input type="submit"></td></tr>'
	print '</table></td>'

def make_graph_multiyear():
	print '<form method="POST" action="year_graph.py">'
	print '<input type="hidden" name="query_option" value="yearly">'
	print '<td>'
	print '<CENTER><H2>Graph yearly data for:</H2>'
	print '<TABLE>'

	functs.form_years()

	functs.form_loop()

	functs.form_stations()

	functs.form_submit()	

	print '</table></td>'


def Main():
	html_setup()
	form = FormContent()
	opt = "daily"
	if form.has_key("opt"):
		opt = form["opt"][0]
	if opt == 'daily':
		make_daily()
	if opt == 'monthly':
		make_monthly()
	if opt == 'yearly':
		make_yearly()
	if opt == 'allstations_daily':
		make_allstations_daily()
	if opt == 'graph_yearly':
		make_graph_yearly()
	if opt == 'graph_multiyear':
		make_graph_multiyear()

	else:
		print '<TD>'
		print '</TD></tr></table>'	



	style.std_bot()

Main()
