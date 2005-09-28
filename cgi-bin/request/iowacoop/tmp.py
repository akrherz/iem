#!/mesonet/python/bin/python
# These are my global functions for Historical search of Iowa Weather
# Daryl Herzmann 3/2/99
# Something is missing / wrong with Corydon...

from cgi import *
import os, re, functs, string

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


def convert_station(code):
        code = code[-4:]
        file = '/home/httpd/html/src/stations.con'
        f = open(file,'r').read()

        lines = re.split('\n',f)
        for i in range(len(lines)):
                line = lines[i]
                info = re.split(',',line)
                if code == info[0]:
                        name = info[3]
        return name




def form_stations():
	stations = functs.stations()
        for i in range(len(stations)):
		station = string.capwords( string.lower(stations[i][0]) )
                print '"'+stations[i][1]+'" => array("city" => "'+station+'","id" => "'+stations[i][1]+'","startYear" => "1893"),'

form_stations()
