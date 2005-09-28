#!/mesonet/python/bin/python
# This program will generate graphs of daily temperature data
# Daryl Herzmann 4-10-99
# 19 May 2003	Allow 2002 data
# 23 Feb 2004	Use makedirs instead

import gd, sys, functs, tempfile, style, os, pg
from cgi import *

mydb = pg.connect('coop', 'db1.mesonet', 5432)

xwidth = 800
yheight = 500

base_fref = '/home/httpd/html/tmp/graphs/'
base_href = '/tmp/graphs/'

def content():
	form = FormContent()
	if form.has_key("city"): 
		city = form["city"][0]
	else:
		style.SendError("Please Enter a City")
	if form.has_key("year"): 
		year = str(form["year"][0])
	else:
		style.SendError("Please Enter a Valid Year")
	if form.has_key("loop"): 
		loop = str(form["loop"][0])
	else:
		loop = 1

	if int(year) < 1893 or int(year) > 2003: 
		style.SendError("Please Enter a Valid Year")


	return city, year, loop

def query_station(city, year):
	results = mydb.query("SELECT high,low from alldata WHERE stationid = '"+city+"' and date_part('year', day) = "+year+" ")
	results = results.getresult()

	return results

def image(city_name, year):
	im = gd.image((xwidth,yheight))

	# Allocate Colors          
	red = im.colorAllocate((255,0,0))
	green = im.colorAllocate((0,255,0))
	blue = im.colorAllocate((0,0,255))
	black = im.colorAllocate((0,0,0))
	white = im.colorAllocate((255,255,255))
	lgreen = im.colorAllocate((127,125,85))

	label = gd.gdFontMediumBold
	title = gd.gdFontGiant

	im.fill((10,10), black)                 # Sets up backround of image

	im.string(title, (10, 5), "Temperature Mins / Maxs for "+city_name+" during "+year , white) 
	im.string(title, (xwidth - 450, yheight - 100), "Consecutive Days", white)
	im.stringUp(title, (0, yheight - 250), "Temperature ", white)

	im.origin((20,0),2,3)

	im.line((0,20),(380,20), lgreen)		# 100 degree line
	im.line((0,88),(380,88), lgreen)		# 32 degree line
	im.line((0,120),(380,120), lgreen)		# 0 degree line

	im.string(label, (0, 16), "100 F", lgreen)
	im.string(label, (0, 84), "32 F", lgreen)
	im.string(label, (0, 116), "0 F", lgreen)


	im.origin((50,0),2,3)

	im.line((90,83),(90,93), white)		# April degree line
	im.line((181,83),(181,93), white)	# July degree line
	im.line((273,83),(273,93), white)	# October degree line

	return im

def parse_data(results):
	highs = []
	lows = []

	for i in range(len(results)):
		highdata = i+1, 120 - int(results[i][0])
		lowdata =  i+1, 120  - int(results[i][1])
		highs.append(highdata)
		lows.append(lowdata)

	return tuple(highs), tuple(lows)

def html_gif(filename):
	print '<HTML>'
	print '<img src="'+filename+'">'

	print '<H3>Options:</H3>'
	print '<P><a href="'+filename+'">Shift-Click to download this graph</a>'
	print '<P><a href="index.py?opt=graph_yearly">Try another query</a>'

def make_animate(dirname):
	os.chdir('/home/httpd/html/tmp/graphs/'+dirname+'/')
	os.popen('/usr/bin/gifsicle --delay=100 --loopcount=3 *.png > anim.gif')

	return '/tmp/graphs/'+dirname+'/anim.gif'

def Main():
	city, year, loop = content()			# Returns forms values
							# City => 3 or 4 digit station code
							# year => 4 digit string for year
							# loop => an interger count variable

	style.header("Historical Iowa WX Data", "white")	# Set up HTML page for apache

	city_name = functs.convert_station(city)	# Convert code into string name of city

	im = []						# Needs an array to set up all the picts

	dirname = tempfile.mktemp()			# Create a directory name via tempfile module
	dirname = dirname[-5:-2] + dirname[-1:]		# I only want intergers in the name

	while (os.path.isdir(base_fref+dirname) ):
		dirname = tempfile.mktemp()                     # Create a directory name via tempfile module
	        dirname = dirname[-5:-2] + dirname[-1:]      

	os.makedirs(base_fref+dirname, 0777)		# Create a directory over in HTML side

	for i in range(int(loop)):			# Create int(loop) number of gif images

		im.append(image(city_name, year))	# Create an image instance to be modified

		results = query_station(city, year)	# Query database system for results
		if len(results) == 0:			# If no results are found, quit the loop
			break				

		highs, lows = parse_data(results)	# Parse out the results into two tuples

		red = im[i].colorAllocate((255,0,0))	# Allocate needed colors for lines on graph
		blue = im[i].colorAllocate((0,0,255))	

		im[i].lines(highs, red)			# High values put on graph in red
		im[i].lines(lows, blue)			# Low values put on graph in blue


		im[i].writePng(base_fref+dirname+"/const"+str(i)+".png")	# Create gif graph

		year = str(int(year)+ 1)		# increment year value by one

	
#	if loop > 0:					# If a loop was needed, then we need to animate it
#		gif_file = make_animate(dirname)	# based on the assumption that all gifs are in one dir
#	else:
	gif_file = base_href+dirname+"/const0.png"	# Otherwise only one gif exists so that is where
								# It is at
	html_gif(gif_file)				# Create the HTML neccessary to view the finished product

	style.std_bot()					# Finish and exit...

Main()
