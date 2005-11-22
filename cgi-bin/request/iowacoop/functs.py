# These are my global functions for Historical search of Iowa Weather
# Daryl Herzmann 3/2/99
# Something is missing / wrong with Corydon...
# 3 Mar 2004	Do some cleanups

from cgi import *
import os, re, functs

def stations():
	stations =  [('Albia','ia0112'),('ALGONA','ia0133'),('Allison','ia0157'),('AMES','ia0200'),('Anamosa','ia0213'),('Ankeny','ia0241'),('ATLANTIC','ia0364'),('Audubon','ia0385'),('Bedford','ia0576'),('Belle-Plaine','ia0600')]
	stations1 = [('Bellevue','ia0608'),('Bloomfield','ia0753'),('Britt','ia0923'),('Carroll','ia1233'),('Cascade','ia1257'),('Castana','ia1277'),('CEDAR RAPIDS','ia1319')]
	stations2 = [('Centerville','ia1354'),('Chariton','ia1394'),('Charles City','ia1402'),('Cherokee','ia1442'),('CLARINDA','ia1533'),('Clarion','ia1541'),('CLINTON','ia1635'),('Colombus Junction','ia1731'),('CORNING','ia1833'),('Cresco','ia1954')]
	stations3 = [('DECORAH','ia2110'),('DENISON','ia2171'),('Dubuque','ia2364'),('Emmetsburg','ia2689'),('Estherville','ia2724'),('FAIRFIELD','ia2789'),('FAYETTE','ia2864'),('Forest City','ia2977'),('Fort Dodge','ia2999'),('Fort Madison','ia3007'),('GLENWOOD','ia3290'),('Greenfield','ia3438')]
	stations4 = [('GRINELL','ia3473'),('Grundy Center','ia3487'),('GUTHRIE CENTER','ia3509'),('Guttenburg','ia3517'),('HAMPTON','ia3584'),('Harlan','ia3632'),('Hawarden','ia3718'),('Humboldt','ia3985'),('Ida Grove','ia4038'),('Independance','ia4052'),('INDIANOLA','ia4063'),('Iowa City','ia4101')]
	stations5 = [('Iowa Falls','ia4142'),('Jefferson','ia4228'),('KEOSAUQUA','ia4389'),('Knoxville','ia4502'),('LEMARS','ia4735'),('LOGAN','ia4894'),('Manchester','ia5086'),('MAQUOKETA','ia5131'),('MARSHALLTOWN','ia5198'),('MASON CITY','ia5230'),('Milford','ia5493'),('MOUNT AYR','ia5769'),('Mount Pleasant','ia5796'),('Muscatine','ia5837')]
	stations6 = [('NEW HAMPTON','ia5952'),('Newton','ia5992'),('Northwood','ia6103'),('Oakland','ia6151'),('Oelwein','ia6200'),('ONAWA','ia6243'),('Osage','ia6305'),('Osceola','ia6316'),('OSKALOOSA','ia6327'),('Perry','ia6566'),('Pocahontas','ia6719'),('Primghar','ia6800'),('Red Oak','ia6940'),('ROCK RAPIDS','ia7147'),('ROCKWELL CITY','ia7161'),('Sac City','ia7312'),('Shenandoah','ia7613'),('Sibley','ia7664'),('Sidney','ia7669')]
	stations7 = [('Sigourney','ia7678'),('Sioux City','ia7708'),('Sioux Rapids','ia7726'),('STORM LAKE','ia7979'),('TIPTON','ia8266'),('Toledo','ia8296'),('Tripoli','ia8339'),('Vinton','ia8568'),('WASHINGTON','ia8688'),('WATERLOO','ia8704'),('Waukon','ia8755'),('WEBSTER CITY','ia8806'),('Williamsburg','ia9067'),('Winterset','ia9132')]

	return stations + stations1 + stations2 + stations3 + stations4 + stations5 + stations6 + stations7

def get_content(field):
        form = FormContent()
        if form.has_key(field):
                return form[field][0]
        else:
                return "None"


def convert_month(month):
        month = month[-2:]
        file = 'months.con'
        f = open(file,'r').read()

        lines = re.split('\n',f)
        for i in range(len(lines)):
                line = lines[i]
                if month == line[-2:]:
                        name = line[:-3]
        return name

def convert_station(code):
        code = code[-4:]
        file = 'stations.con'
        f = open(file,'r').read()

        lines = re.split('\n',f)
        for i in range(len(lines)):
                line = lines[i]
                info = re.split(',',line)
                if code == info[0]:
                        name = info[3]
        return name


def form_days():
	print '<tr><th>Select a day:</th>'
        print '<td><SELECT name="day">'
        for i in range(31):
                i = str(i+1)
                print '<option value="'+i+'">'+i
        print '</SELECT></td></tr>'


def form_stations():
	stations = functs.stations()
	print '<tr><th>Select a Station:</th>'   
        print '<td><SELECT name="city" size="6">'
        for i in range(len(stations)):
                print '<option value="'+stations[i][1]+'">'+stations[i][0]
        print '</SELECT></td></tr>'

def form_months():
	print '<TR><TH>Select a month:</TH>'
        print '<td><SELECT name="month">'
        months = ('January','February','March','April','May','June','July','August','September','October','November','December')
	for i in range(12):
                j = str(i+1)
                print '<option value="'+j+'">'+months[i]
        print '</SELECT></td></tr>'

def form_years():
	print '<TR><TD colspan="2"><B>Note:</B>  Not all stations contain data back till 1893.'
	print ' Only stations in capital letters contain all data since 1893, the rest date back to 1951.</TD></TR>'
	print '<TR><TH>Enter a Year between 1893 - 2004:</TH>'
        print '<td><input type="text" size="4" name="year"></td></tr>'
	print '<input type="hidden" loop="0">'

def form_submit():
	print '<tr><th>Submit Search:</th>'
        print '<td><input type="submit"></td></tr>'

def form_loop():
	print '<TR><TH>Enter the number of years to loop:</TH>'
        print '<td><input type="text" size="3" name="loop"></td></tr>'

