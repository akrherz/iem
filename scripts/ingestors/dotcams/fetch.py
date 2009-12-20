from twisted.internet import reactor
from twisted.web import client
import urllib, simplejson

def test(data):
  print data

#payload = urllib.urlencode({'Mode': 1,\
payload = simplejson.dumps({'Mode': 1,\
                            'SiteID': 357,\
                            'Type': 'Rwis',
                            'CameraID': 1})
url = 'http://weatherview.iowadot.gov/DetailPage.aspx/GetSlides'
client.getPage(url, postdata=payload, method='POST',
  headers={'Content-Type': 'application/json; charset=utf-8'}
  ).addCallback( test ).addErrback( test )


reactor.run()
