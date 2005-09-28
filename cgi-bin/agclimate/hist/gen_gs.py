#!/mesonet/python/bin/python
# This is the program that will create gs chart for the kiddies
# Daryl Herzmann 10-17-99


import cgi, time, tempfile, mod_prec, mod_soilgdd, mod_gdd, style

def gen_filename():
	dirname = tempfile.mktemp()
	dirname = dirname[-5:-2] + dirname[-1:]
	return "/mesonet/www/html/agclimate/hist/tmp/"+dirname+".png", "/agclimate/hist/tmp/"+dirname+".png"

def Main():
	form = cgi.FormContent()
	yeer = form["yeer"][0]
	start_month = form["start_month"][0]
	end_month = form["end_month"][0]
	start_day = form["start_day"][0]
	end_day = form["end_day"][0]
	type = form["type"][0]
	
	tmpfile, html_href = gen_filename()
	
	print 'Content-type: text/html \n\n'
	
	if type == "GDD":		# Air GDD
		filename = mod_gdd.Main(tmpfile, yeer, start_month, end_month, start_day, end_day, "Total GDDs", "c11, c12")
	elif type == "SGDD":		# Soil GDD
		filename = mod_soilgdd.Main(tmpfile, yeer, start_month, end_month, start_day, end_day, "Total Soil GDD", "c300")
	elif type == "PREC":		# Precipation
		filename = mod_prec.Main(tmpfile, yeer, start_month, end_month, start_day, end_day, "Total Precip", "c90")
	elif type == "ET":		# Evapo-Transpiration
		filename = mod_prec.Main(tmpfile, yeer, start_month, end_month, start_day, end_day, "Total ET", "c70")
		
	
	print '<img src="'+html_href+'">'	

Main()
