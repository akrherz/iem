"""
Example script that scrapes data from the IEM ASOS download service
"""
from __future__ import print_function
import json
import time
import datetime

"Libraries that follows should be within Python Standard Library" 
import argparse
import codecs
import csv
import datetime


# Python 2 and 3: alternative 4
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

# Number of attempts to download data
MAX_ATTEMPTS = 6
# HTTPS here can be problematic for installs that don't have Lets Encrypt CA
SERVICE = "http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"


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
            data = urlopen(uri, timeout=300).read().decode("utf-8")
            if data is not None and not data.startswith("ERROR"):
                return data
        except Exception as exp:
            print("download_data(%s) failed with %s" % (uri, exp))
            time.sleep(5)
        attempt += 1

    print("Exhausted attempts to download, returning empty data")
    return ""


def get_stations_from_filelist(filename):
    """Build a listing of stations from a simple file listing the stations.

    The file should simply have one station per line.
    """
    stations = []
    for line in open(filename):
        stations.append(line.strip())
    return stations


def get_stations_from_networks():
    """Build a station list by using a bunch of IEM networks."""
    stations = []
    states = """AK AL AR AZ CA CO CT DE FL GA HI IA ID IL IN KS KY LA MA MD ME
     MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT
     WA WI WV WY"""
    networks = []
    for state in states.split():
        networks.append("%s_ASOS" % (state,))

    for network in networks:
        # Get metadata
        uri = (
            "https://mesonet.agron.iastate.edu/geojson/network/%s.geojson"
        ) % (network,)
        data = urlopen(uri)
        jdict = json.load(data)
        for site in jdict["features"]:
            stations.append(site["properties"]["sid"])
    return stations


def download_alldata():
    """An alternative method that fetches all available data.

    Service supports up to 24 hours worth of data at a time."""
    # timestamps in UTC to request data for
    startts = datetime.datetime(2012, 8, 1)
    endts = datetime.datetime(2012, 9, 1)
    interval = datetime.timedelta(hours=24)

    service = SERVICE + "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

    now = startts
    while now < endts:
        thisurl = service
        thisurl += now.strftime("year1=%Y&month1=%m&day1=%d&")
        thisurl += (now + interval).strftime("year2=%Y&month2=%m&day2=%d&")
        print("Downloading: %s" % (now,))
        data = download_data(thisurl)
        outfn = "%s.txt" % (now.strftime("%Y%m%d"),)
        with open(outfn, "w") as fh:
            fh.write(data)
        now += interval

def construct_urls(station, start_date, finish_date):
    '''
    This function allows you to construct a list of URLs for a list of stations and start dates.
    This is also written using Python 3.6 and later, did not add a checker but one could be added in
    the future to ensure you're using a newer version of Python. 
    
    A checker to see if airports are within IEM database could be added if needed.

    Args:
    station: a list or tuple of strings containing the 4 letter airport/station code.
    start_date: a datetime.datetime of the calendar date of the start date. Format (year,month,day)
    finish_date: a datetime.datetime of the calendar date of the end date. Format (year,month,day)

    Returns:
      A list of urls.
    '''
    
    if not isinstance(station, (list, tuple)):
        raise TypeError(f'Station must be a {list} or {tuple}.')

    if not all(isinstance(x, str) for x in station):
        raise TypeError(f'Station elements must be a list all being {str}')

    if start_date > datetime.datetime.now():
        raise ValueError(f'Starting date {start_date} is in the future.')

    if finish_date > datetime.datetime.now():
        raise ValueError(f'End date {finish_date} is in the future.')

    if start_date > finish_date:
        raise ValueError(
            f'Start date {start_date} is past your finish_date {finish_date}')

    try:

        SERVICE = "http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
        service = SERVICE + "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

        service += start_date.strftime("year1=%Y&month1=%m&day1=%d&")
        service += finish_date.strftime("year2=%Y&month2=%m&day2=%d&")
        return [f"{service}&station={station}" for station in station]

    except Exception as exp:
        print(f"""Bad data with: {station} - using {start_date}
        and {finish_date}.\nException raised {exp}.""")

 def pull_metar(url):
    '''
    This function simply returns a Pandas DataFrame for a requested URL.

    Args:
      url: takes a url string that contains a .csv file.

    Returns:
      A list of tuples.
    '''

    response = urlopen(url)
    csvfile = csv.reader(codecs.iterdecode(response, "utf-8"))
    list_of_tuples = list(map(tuple, csvfile))

    # If the user wants to strip the DEBUG info given, use the del command below.
    # del list_of_tuples[0:5]
    return list_of_tuples

def main():
    """Our main method"""
    # timestamps in UTC to request data for
    startts = datetime.datetime(2012, 8, 1)
    endts = datetime.datetime(2012, 9, 1)

    service = SERVICE + "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

    service += startts.strftime("year1=%Y&month1=%m&day1=%d&")
    service += endts.strftime("year2=%Y&month2=%m&day2=%d&")

    # Two examples of how to specify a list of stations
    stations = get_stations_from_networks()
    # stations = get_stations_from_filelist("mystations.txt")
    for station in stations:
        uri = "%s&station=%s" % (service, station)
        print("Downloading: %s" % (station,))
        data = download_data(uri)
        outfn = "%s_%s_%s.txt" % (
            station,
            startts.strftime("%Y%m%d%H%M"),
            endts.strftime("%Y%m%d%H%M"),
        )
        out = open(outfn, "w")
        out.write(data)
        out.close()


if __name__ == "__main__":
    download_alldata()
    # main()

    
'''
Example use case of using the construct_urls and pull_metar functions. 

def main():
    '''Takes start and finish dates from command line, then passes it to retrieve the metars.'''

    # Takes in user input for the start and end dates.
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', nargs='+', type=int)
    parser.add_argument('--finish', nargs='+', type=int)
    args = parser.parse_args()
    start = datetime.datetime(*args.start)
    finish = datetime.datetime(*args.finish)

    metar = []
    # Can pull in from file, just needs to be List or Tuple.
    station = ["CYOW", "CYYZ"]
    
    url = construct_urls(station, start, finish)

    for i in url:
        metar += pull_metar(i)

    print(f"URL constructed is:\n{chr(10).join(url)} \n")
    print(
        f'CSV file in a list of tuples is:\n{chr(10).join(repr(x) for x in metar)}')


if __name__ == "__main__":
    main()
'''
    
