''' Fill in the missing lat/lon values '''

import urllib2
import json
import time

out = open('step2.csv', 'w')
cnt = 0
for linenum, line in enumerate(open('daryl_corey_data_110513.csv')):
    if linenum == 0:
        continue
    tokens = line.split(",")
    zipcode = tokens[11]
    lon = tokens[13]
    lat = tokens[12]
    if (lat == '' or lon == '') and zipcode != '':
        cnt += 1
        uri = ('http://maps.googleapis.com/maps/api/geocode/json'
               +'?address='+zipcode+'&sensor=true')
        data = json.loads( urllib2.urlopen(uri).read() )
        if len(data['results']) > 0:
            print zipcode, data['results'][0]['geometry']['location']
            tokens[13] = "%.4f" % (data['results'][0]['geometry']['location']['lng'],)
            tokens[12] = "%.4f" % (data['results'][0]['geometry']['location']['lat'],)
        else:
            print 'Failure %s' % (zipcode,), data

        time.sleep(1)
    out.write(",".join(tokens))
    
out.close()
print 'Geocoded %s' % (cnt,)