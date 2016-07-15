import datetime
import requests
import urllib2

modelts = datetime.datetime(2016, 7, 15, 0)
fts = datetime.datetime(2016, 7, 22, 21)
fhour = (fts - modelts).total_seconds() / 3600
print "Fhour %s" % (fhour,)
fhourstr = "%03i" % (fhour,)

uri = modelts.strftime(("http://ftpprd.ncep.noaa.gov/data/nccf/com/gfs/"
                        "prod/gfs.%Y%m%d%H/gfs.t%Hz.pgrb2.0p25."
                        "f" + fhourstr + ".idx"))
r = requests.get(uri)

offsets = []
neednext = False
for line in r.content.split("\n"):
    tokens = line.split(":")
    if len(tokens) < 5:
        continue
    if neednext:
        offsets[-1].append(int(tokens[1]))
        neednext = False
    if tokens[3] == 'TMP' and tokens[4] == '2 m above ground':
        offsets.append([int(tokens[1]), ])
        neednext = True

req = urllib2.Request(uri[:-4])
pr = offsets[0]
req.headers['Range'] = 'bytes=%s-%s' % (pr[0], pr[1])
output = open('gfs.grib', 'wb', 0664)
f = urllib2.urlopen(req, timeout=30)
output.write(f.read())
output.close()
