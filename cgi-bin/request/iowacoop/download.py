#!/mesonet/python/bin/python
# This will be the script that runs for users to download data files
# Daryl Herzmann 3/31/99
#  3 Apr 2003	Print a header on this file to avoid confusion with the
#		climoweek data that is printed in the output

import functs, style, os, tempfile, shutil, engine, cgi


filename = tempfile.mktemp()
filename = filename[-5:-2] + filename[-1:]
shutil.copy('/home/httpd/html/src/ex.txt','/home/httpd/html/tmp/'+filename+'.txt')
file = open('/home/httpd/html/tmp/'+filename+'.txt','w')


def Main():
	style.header("Download Dataset from IowaWx Archive","white")
	print '<H2>Instructions for downloading the data</H2>'

	query_option = functs.get_content("query_option")
	city = functs.get_content("city")
	year = functs.get_content("year")
	month = functs.get_content("month")
	day = functs.get_content("day")

	if month == "None":
		str_month = "None"
	else:
		str_month = functs.convert_month("0"+month)

	if city == "None":
		str_city = "None"
	else:
		str_city = functs.convert_station(city)

	print '<HR><H3>1. Review Search Parameters....</H3>'
	print '<TABLE NOBORDER>'
        print '<TR><TH colspan="4">Search Paramenters:</TH><TH colspan="6"><font color="red">Time Constraints:</red></TH></TR>'
        print '<TR><TH bgcolor="#EEEEE">Query Option:</TH><TD>'+query_option+'</TD>'
        print '<TH bgcolor="#EEEEE">Station Option:</TH><TD>'+str_city+'</TD>'
        print '<TH bgcolor="#EEEEE"><font color="red">Year:</font></TH><TD>'+year+'</TD>'
        print '<TH bgcolor="#EEEEE"><font color="red">Month:</font></TH><TD>'+str_month+'</TD>'
        print '<TH bgcolor="#EEEEE"><font color="red">Day:</font></TH><TD>'+day+'</TD>'
        print '</TR></TABLE>'
        print '<HR>'

	print '<H3>2. Instructions for downloading this data.</H3>'
	print 'Below a link with appear and you need to hold the shift key down and click on the link.<BR>'
	print 'This should allow you to save the text file locally, so then you can do what ever you want with it.<BR>'
	print '<HR>'

	url = '/tmp/'+filename+'.txt'

	print '<H3>3. Creating data file... (May take a few seconds.)</H3>'


	results = engine.search(query_option, city, year, month, day)

        file.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % ('COOP_ID', 'DATE', \
          'CLIMO_WEEK', 'HIGH', 'LOW', 'RAINFALL', 'SNOWFALL') )

	for i in range(len(results)):
		city = results[i][0]
		day = results[i][1]
		climoweek = str(results[i][2])
		high  = str(results[i][3])
		low = str(results[i][4])
		rain = str(results[i][5])
		snow = str(results[i][6])
		file.write(city+'\t'+day+'\t'+climoweek+'\t'+high+'\t')
		file.write(low+'\t'+rain+'\t'+snow+'\n')
	file.close()

	print '<BR>File created successfully!! <BR><HR>'

	print '<H3>4. Download file</H3>'
	print '<a href="'+url+'">Shift-Click Here, to download file</a><BR>'

	print '<p><a href="index.py">Return to COOP data query</a>'

	style.std_bot()

Main()
