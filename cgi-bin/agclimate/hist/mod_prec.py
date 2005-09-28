#!/mesonet/python/bin/python
# This program will make the GS precipation totals
# Daryl Herzmann 10-17-99
# This adds up and plots data as needed...

import gd, time, style
from campbell import *

iowa_gif_src = "/mesonet/www/html/agclimate/src/iowa.png"

locations = alt_locations

def mk_image(im, yeer, start_month, end_month, start_day, end_day, str_title):

	white = im.colorAllocate((255,255,255))	# Colors to use in the image
	black = im.colorAllocate((0,0,0))	# Colors to use in the image

	start_tuple = (int(yeer), int(start_month), int(start_day), 0, 0, 0, 0, 0, 0)
        end_tuple = (int(yeer), int(end_month), int(end_day), 0, 0, 0, 0, 0, 0)


	nice_date = time.strftime("%B %d, %Y", start_tuple)			# Nice format for graph title
	today = time.strftime("%B %d, %Y", end_tuple)
	im.string(title, (45,15), str_title , black) # The actual title
	im.string(title, (115,60), "("+nice_date+" thru "+today+")" , black) # The actual title
	im.string(title, (210,434), "[inches]", black)

	nice_date = time.strftime("%x %X", now_tuple)			# My Timestamp date format
	im.string(label, (290,490), "Generated on "+nice_date, black)	# My Timestamp label

	return im	# Return image container for others to fill

def plot_pt(im, c90, location):
	red = im.colorAllocate((255,0,0))	# Colors to use in the image

	im.string(title, (location[0], location[1]), str(round(c90, 2)), red)		# High Temp.

	return im	# Return image container for others to fill

def Main(tmpfile, yeer, start_month, end_month, start_day, end_day, str_title, data_code):
	im = gd.image(iowa_gif_src) 	# load image into a gd container
	im = mk_image(im, yeer, start_month, end_month, start_day, end_day, str_title)

	start_tuple = (int(yeer), int(start_month), int(start_day), 0, 0, 0, 0, 0, 0)
        end_tuple = (int(yeer), int(end_month), int(end_day), 0, 0, 0, 0, 0, 0)

	start_secs = time.mktime(start_tuple)
        end_secs = time.mktime(end_tuple)

        if start_secs > end_secs:
                style.SendError("Go back and check your dates.")

        days = int((end_secs - start_secs)/86400)


	i = 0	# loop variable
	for station in stations:
		tot = 0
		for day in range(0, days+1):
			c90 = 0
			this_sec = start_secs + (86400 * day)
                	local = time.localtime(this_sec)
                	yeer = time.strftime("%Y", local)
                	month = time.strftime("%m", local)
                	day = time.strftime("%d", local)
                	sation = station+"_"+yeer
			dateStr = month+"-"+day+"-"+yeer
			try:
				query = mydb.query("SELECT "+data_code+" from "+station+"_"+yeer+" WHERE day = '"+dateStr+"' ").getresult()
			except:
				continue
			try:
				c90 = float(query[0][0])			# radiation
			except:
				hi = "Hello"
			tot = tot + c90
		im = plot_pt(im, tot, locations[i])	# my ploting function
		i = i + 1				# Increment variable

	im.writePng(tmpfile)			# Write file out

# I need to get a mention for doing all stations
#	print '<a href="/cgi-bin/agclimate/hist/req_data.py?start_year='+yeer+'&end_year='+yeer+'&start_day='+start_day+'&end_month='+end_month+'&start_month='+start_month+'&end_day='+end_day+'&db=campbell_daily&data_type=c90">Clickme for the Raw Data</a>'

