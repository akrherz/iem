#!/usr/local/bin/python
# This program will generate any map apon request
# Daryl Herzmann 6/22/99
# UPDATED 7-11-99: Gonna make this work completely, with any argument
# 27 Aug 2001:	Problem with plotting dates in which all the stations
#		did not exist...

import tempfile, sys, re, string
from campbell import *
from cgi import *

dirname = tempfile.mktemp()                     # Create a directory name via tempfile module
dirname = dirname[-5:-2] + dirname[-1:] 

iowa_gif_src = "/mesonet/www/html/agclimate/src/iowa.png"
iowa_gif_out = "/mesonet/www/html/agclimate/hist/tmp/"+dirname+".png"
iowa_gif_href = "/agclimate/hist/tmp/"+dirname+".png"

def mk_image(im):
	black = im.colorAllocate((0,0,0))	# Colors to use in the image
	red = im.colorAllocate((255,0,0))	#
	blue = im.colorAllocate((0,0,255))	#

	nice_date = time.strftime("%x %X", now_tuple)			# My Timestamp date format
	im.string(label, (290,490), "Generated on "+nice_date, black)	# My Timestamp label

	return im	# Return image container for others to fill

def plot_pt(im, first, second, location):
	red = im.colorAllocate((255,0,0))	# Colors to use in the image
	blue = im.colorAllocate((0,0,255))	#

	if len(str(first)) != 0:
		im.string(title, (location[0], location[1]), str(first), red)		# High Temp.

	if len(str(second)) != 0:
		im.string(title, (location[0], location[1]+off), str(second), blue)		# Low Temp.

	return im	# Return image container for others to fill

def plot(data, secs):
#	print 'Content-type: text/html \n\n'
#	print '<HTML>'

#	form = FormContent()
#	yeer = form["yeer"][0]
#	month = form["month"][0]
#	day = form["day"][0]
#	data = form["data"][0]

	im = gd.image(iowa_gif_src) 	# load image into a gd container
	im = mk_image(im)

#	time_tuple = (int(yeer), int(month), int(day),  12, 36, 20, 4, 127, 1)
	time_tuple = time.localtime(float(secs))
	nice_date = time.strftime("%B %d, %Y", time_tuple)			# Nice format for graph title
	yeer = time.strftime("%Y", time_tuple)
	month = time.strftime("%m", time_tuple)
	day = time.strftime("%d", time_tuple)

	black = im.colorAllocate((0,0,0))	# Colors to use in the image
	title_str = titles[data]
	label_str = labels[data]
	im.string(title, (15,15), title_str+nice_date , black) # The actual title
	im.string(title, (200,440), label_str, black)

	round_int = int(rounds[data])

	dateStr = str(month)+"-"+str(day)+"-"+str(yeer)

	i = 0	# loop variable
	for station in stations:
		if data == "c300":
			try:
				query = mydb2.query("SELECT "+data+" from "+station+"_"+yeer+" WHERE (date(day) = '"+dateStr+"' )").getresult()
			except:
				continue			

			query.sort()
			second = int(float( query[0][0]))
			first = int(float( query[23][0]))

		elif data == "c1":
			try:
				query = mydb2.query("select MAX( k2f( dewpt( f2k(c100), c200)))::numeric(7,2) as c1, \
					MIN( k2f( dewpt( f2k(c100), c200)))::numeric(7,2) as c2 \
					from "+station+"_"+yeer+" WHERE date(day) = '"+dateStr+"' ").getresult()
				query.sort()
				second = int(float( query[0][1]))
				first = int(float( query[0][0]))
			except:
				second = 0
				first = 0

		else:
			try:
				query = mydb.query("SELECT "+data+" from "+station+"_"+yeer+" WHERE (day = '"+dateStr+"')").getresult()
			except:
				continue


			try:
				first = float(query[0][0])
				first = round(first, round_int)
				if round_int == 0:
					first = int(first)
	
			except IndexError:
				first = ""
			try:
				second = float(query[0][1])
				second = str(round(second, round_int))
				if second[-2:] == ".0" and data == "c529, c530":
					second = ("00"+second[:-2])[-4:]	# Get the damn times straighten out
				elif round_int == 0:
					second = int(float(second))

			except IndexError:
				second = ""	# low air-temp


		im = plot_pt(im, first, second, locations[i]) # my ploting function
		i = i + 1		# Increment variable

	im.writePng(iowa_gif_out)	# Write file out

	print '<img src="'+iowa_gif_href+'">'
#	print '</HTML>'

