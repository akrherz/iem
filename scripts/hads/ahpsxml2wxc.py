"""Convert the AHPS XML into WXC format"""

import urllib2
import datetime
from twisted.words.xish import domish, xpath

xml = urllib2.urlopen('http://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=mroi4&output=xml').read()
elementStream = domish.elementStream()
roots = []
results = []
elementStream.DocumentStartEvent = roots.append
elementStream.ElementEvent = lambda elem: roots[0].addChild(elem)
elementStream.DocumentEndEvent = lambda: results.append(roots[0])

print """IEM MROI4 Test host=273805670 TimeStamp=2015-12-17T09:34:27
    4
    15 Station
     5 LocalTime
     7 Stage
     7 CFS"""

elementStream.parse(xml)
elem = results[0]
nodes = xpath.queryForNodes('/site/forecast/datum', elem)
i = 0
for node in nodes:
    utc = datetime.datetime.strptime(str(node.valid)[:15], '%Y-%m-%dT%H:%M')
    print "%12s%03i %5s %7s %7s" % ('MROI4', i, utc.strftime("%I %p"),
                                    node.primary, node.secondary)
    i += 1
