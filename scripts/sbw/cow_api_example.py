"""Scrape IEM Cow's API for goodies

License:
  Apache 2.0

Author:
  daryl herzmann akrherz@iastate.edu
"""
from __future__ import print_function
import json
# Python 2 and 3: alternative 4
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


def main():
    """Example"""
    # query IEM service to return a list of WFOs
    uri = "https://mesonet.agron.iastate.edu/geojson/network/WFO.geojson"
    data = urlopen(uri)
    jdict = json.load(data)
    for site in jdict['features']:
        wfo = site['properties']['sid']
        sitename = site['properties']['sname']

        endpoint = ("https://mesonet.agron.iastate.edu/api/1/cow.json?"
                    "begints=2018-07-01T00:00Z&endts=2018-07-31T23:59Z&"
                    "phenomena=TO&lsrtype=TO&wfo=%s" % (wfo, ))
        cowdata = urlopen(endpoint)
        cowdict = json.load(cowdata)
        # print(json.dumps(cowdict, indent=2))
        print(("%s %s issued %s Tornado Warnings this July"
               ) % (wfo, sitename, cowdict['stats']['events_total']))


if __name__ == '__main__':
    main()
