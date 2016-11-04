"""
  Example script that uses IEM APIs to download raw RIDGE images from my
  archive
"""

import urllib2
import urllib
import json
import datetime

now = datetime.date(2009,1,1)
ets = datetime.date(2014,1,1)

URI = "https://mesonet.agron.iastate.edu/json/radar?"
RADAR = "EAX"
PRODUCT = "N0Z"

while now < ets:
    print 'Fetching %s-%s tiles for %s' % (RADAR, PRODUCT, now)
    getvars = {'operation': 'list',
               'radar': RADAR,
               'product': PRODUCT,
               'start': "%sT00:00Z" % (now.strftime("%Y-%m-%d"),),
               'end': "%sT00:00Z" % ((now +
                    datetime.timedelta(days=1)).strftime("%Y-%m-%d"),),               
    }
    
    thisurl = URI + urllib.urlencode(getvars)
    data = urllib2.urlopen(thisurl).read()
    
    j = json.loads(data)
    for scan in j['scans']:
        valid = datetime.datetime.strptime(scan['ts'], '%Y-%m-%dT%H:%MZ')

        #for suffix in ['png', 'wld']:
        for suffix in ['png',]:
            tileuri = valid.strftime(("https://mesonet.agron.iastate.edu/archive/"
                    +"data/%Y/%m/%d/GIS/ridge/"+RADAR+"/"+PRODUCT+"/"+RADAR
                    +"_"+PRODUCT+"_%Y%m%d%H%M."+suffix))
        
            localfn = valid.strftime(RADAR+"_"+PRODUCT+"_%Y%m%d%H%M."+suffix)
            fp = urllib2.urlopen(tileuri).read()
            output = open(localfn, 'w')
            output.write( fp )
            output.close()
    
    now += datetime.timedelta(days=1)