#!/mesonet/python/bin/python
# This program will calculate the Soil GDD's
# Daryl Herzmann 6-22-99
# UPDATED 6/23/99: Cleaned up code and changed crawfordsville point
# UPDATED 7/8/99: Making this script work

import gd, time, style
from campbell import *

iowa_gif_src = "/mesonet/www/html/agclimate/src/iowa.png"

locations = alt_locations

def mk_image(im, yeer, start_month, end_month, start_day, end_day, str_title):
	white = im.colorAllocate((255,255,255)) # Colors to use in the image
	black = im.colorAllocate((0,0,0))	# Colors to use in the image

        start_tuple = (int(yeer), int(start_month), int(start_day), 0, 0, 0, 0, 0, 0)
        end_tuple = (int(yeer), int(end_month), int(end_day), 0, 0, 0, 0, 0, 0)

	nice_date = time.strftime("%B %d, %Y", start_tuple)			# Nice format for graph title
        today = time.strftime("%B %d, %Y", end_tuple)
	im.string(title, (5,15), str_title ,black) # The actual title
	im.string(title, (120,60), "("+nice_date+" thru "+today+")" , black) # The actual title
	im.string(title, (205,435), "[GDDs]", black)

	nice_date = time.strftime("%x %X", now_tuple)			# My Timestamp date format
	im.string(label, (290,490), "Generated on "+nice_date, black)	# My Timestamp label

	return im	# Return image container for others to fill

def plot_pt(im, c90, location):
	red = im.colorAllocate((255,0,0))	# Colors to use in the image

	im.string(title, (location[0], location[1]), str(c90), red)		# High Temp.

	return im	# Return image container for others to fill

def Main(tmpfile, yeer, start_month, end_month, start_day, end_day, str_title, data_code):
        im = gd.image(iowa_gif_src)     # load image into a gd container
        im = mk_image(im, yeer, start_month, end_month, start_day, end_day, str_title)

        start_tuple = (int(yeer), int(start_month), int(start_day), 0, 0, 0, 0, 0, 0)
        end_tuple = (int(yeer), int(end_month), int(end_day), 0, 0, 0, 0, 0, 0)

        start_secs = time.mktime(start_tuple)
        end_secs = time.mktime(end_tuple)

        if start_secs > end_secs:
                style.SendError("Go back and check your dates.")

        days = int((end_secs - start_secs)/86400)

        i = 0   # loop variable
        for station in stations:
                tot = 0
		for day in range(0, days+1):
                        this_sec = start_secs + (86400 * day)
                        local = time.localtime(this_sec)
                        year = time.strftime("%Y", local)
                        month = time.strftime("%m", local)
                        day = time.strftime("%d", local)
                        sation = station+"_"+year
			dateStr = month+"-"+day+"-"+year
			try:
	                        query = mydb2.query("SELECT "+data_code+" from "+station+"_"+yeer+" WHERE date(day) = '"+dateStr+"' ").getresult()
				query.sort()
			except:
				continue

			try:
				high = int(float(query[0][0]))			# radiation
				low = int(float(query[23][0]))		# radiation
			except:
				Hello = "Hi"

			if low < 50:		# The low is always at least 50
				low = 50
			if high > 86: 
				high = 86
			if high < 50:		# If the high is lower than 50, than no Gdd's
				this_gdd = 0			
			else:
				this_gdd = ((high+low)/2) - 50
			
			tot = tot + this_gdd

		im = plot_pt(im, int( float(tot)), locations[i])	# my ploting function
		i = i + 1				# Increment variable

	im.writePng(tmpfile)			# Write file out


