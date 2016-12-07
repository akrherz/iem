"""
Example script that scrapes data from the IEM ASOS download service
"""
import json
import datetime
import urllib2

# timestamps in UTC to request data for
startts = datetime.datetime(2012, 8, 1)
endts = datetime.datetime(2012, 9, 1)

SERVICE = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
SERVICE += "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

SERVICE += startts.strftime('year1=%Y&month1=%m&day1=%d&')
SERVICE += endts.strftime('year2=%Y&month2=%m&day2=%d&')

states = """AK AL AR AZ CA CO CT DE FL GA HI IA ID IL IN KS KY LA MA MD ME
 MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT
 WA WI WV WY"""
# IEM quirk to have Iowa AWOS sites in its own labeled network
networks = ['AWOS']
for state in states.split():
    networks.append("%s_ASOS" % (state,))

for network in networks:
    # Get metadata
    uri = ("https://mesonet.agron.iastate.edu/"
           "geojson/network/%s.geojson") % (network,)
    data = urllib2.urlopen(uri)
    jdict = json.load(data)
    for site in jdict['features']:
        faaid = site['properties']['sid']
        sitename = site['properties']['sname']
        uri = '%s&station=%s' % (SERVICE, faaid)
        print 'Network: %s Downloading: %s [%s]' % (network, sitename, faaid)
        data = urllib2.urlopen(uri)
        outfn = '%s_%s_%s.txt' % (faaid, startts.strftime("%Y%m%d%H%M"),
                                  endts.strftime("%Y%m%d%H%M"))
        out = open(outfn, 'w')
        out.write(data.read())
        out.close()
