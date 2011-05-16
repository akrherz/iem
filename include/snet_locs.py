import sys, string
from pyIEM import iemdb
i = iemdb.iemdb()
mydb = i['mesosite']

def to_lower(s):
    if s == None:    return "none"
    return string.lower(s)

format = '"%s" => array("short" => "%s", "online" => "%s", "city" => "%s", "nwn_id" => "%s", "lat" => "%s", "lon" => "%s", "network" => "%s", "county" => "%s", "climate_site" => "%s"),'

print """<?php 
/* Auto generated from snet_locs.py */
$cities = Array( 
"""

for tv in ('KCCI','KELO','KIMT'):
    print "'%s' => Array(" % (tv,)
    rs = mydb.query("SELECT *, y(geom) as latitude, x(geom) as longitude from stations \
      WHERE network = '%s' ORDER by name" % (tv,) ).dictresult()

    for i in range(len(rs)):
        print format % (rs[i]["id"], rs[i]["plot_name"], rs[i]['online'], \
    rs[i]["name"], rs[i]['nwn_id'], \
    rs[i]["latitude"], rs[i]["longitude"], rs[i]["network"], rs[i]["county"], \
    to_lower(rs[i]["climate_site"]) )

    print "),"
print "); "

print "$Sconv = Array("

sql = "SELECT id, nwn_id from stations WHERE network IN ('KCCI','KELO','KIMT') ORDER by nwn_id ASC"
rs = mydb.query(sql).dictresult()
for i in range(len(rs)):
    print "%s => '%s'," % (rs[i]['nwn_id'], rs[i]['id'])

print "); "
print "?>"