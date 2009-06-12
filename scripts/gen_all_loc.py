#!/mesonet/python/bin/python
# 5 May 2004	Include climate_site reference!

import sys, string

#from pyIEM import iemdb
#i = iemdb.iemdb()
#mydb = i['mesosite']

import pg
mydb = pg.connect('mesosite', 'iemdb', user='nobody')

def to_lower(s):
	if s == None:	return "none"
	return string.lower(s)

rs = mydb.query("SELECT * from stations \
  WHERE network != 'NEXRAD' and network != 'WFO' ORDER by name").dictresult()

format = '"%s" => array("city" => "%s", "id" => "%s", "lat" => "%s", "lon" => "%s", "network" => "%s", "county" => "%s", "climate_site" => "%s"),\n'

out = open("../include/all_locs.php", 'w')

out.write("<?php $cities = Array( \n")

for i in range(len(rs)):
  out.write(format % (rs[i]["id"], rs[i]["name"], rs[i]["id"], rs[i]["latitude"], \
    rs[i]["longitude"], rs[i]["network"], rs[i]["county"], \
	to_lower(rs[i]["climate_site"]) ) )

out.write("); ?>\n")
out.close()
