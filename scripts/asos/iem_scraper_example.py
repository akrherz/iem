"""
Example script that scrapes data from the IEM ASOS download service
"""
from __future__ import print_function
import json
import time
import datetime
import urllib2

# Number of attempts to download data
MAX_ATTEMPTS = 6
SERVICE = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"


def download_data(uri):
    """Fetch the data from the IEM

    The IEM download service has some protections in place to keep the number
    of inbound requests in check.  This function implements an exponential
    backoff to keep individual downloads from erroring.

    Args:
      uri (string): URL to fetch

    Returns:
      string data
    """
    attempt = 0
    while attempt < MAX_ATTEMPTS:
        try:
            data = urllib2.urlopen(uri, timeout=300).read()
            if data is not None and not data.startswith('ERROR'):
                return data
        except Exception as exp:
            print("download_data(%s) failed with %s" % (uri, exp))
            time.sleep(5)
        attempt += 1

    print("Exhausted attempts to download, returning empty data")
    return ""


def main():
    # timestamps in UTC to request data for
    startts = datetime.datetime(2012, 8, 1)
    endts = datetime.datetime(2012, 9, 1)

    service = SERVICE + "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

    service += startts.strftime('year1=%Y&month1=%m&day1=%d&')
    service += endts.strftime('year2=%Y&month2=%m&day2=%d&')

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
            uri = '%s&station=%s' % (service, faaid)
            print(('Network: %s Downloading: %s [%s]'
                   ) % (network, sitename, faaid))
            data = download_data(uri)
            outfn = '%s_%s_%s.txt' % (faaid, startts.strftime("%Y%m%d%H%M"),
                                      endts.strftime("%Y%m%d%H%M"))
            out = open(outfn, 'w')
            out.write(data)
            out.close()


if __name__ == '__main__':
    main()
