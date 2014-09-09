
import datetime
import urllib2

now = datetime.datetime(2014,3,1)
ets = datetime.datetime(2014,8,31)

while now <= ets:
    print "Fetching %s" % ( now.strftime("%d %b %Y"), )
    uri = now.strftime(("http://mesonet.agron.iastate.edu/rainfall/"
          +"dshape.php?month=%m&day=%d&year=%Y&geometry=point&"
          +"duration=day&epsg=4326"))
    data = urllib2.urlopen(uri).read()
    o = open("%s_rain.zip" % (now.strftime("%Y%m%d"),), 'wb')
    o.write(data)
    o.close()

    now += datetime.timedelta(days=1)
