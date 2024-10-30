"""
An example script to sequentially download data from a bunch of long term
ASOS sites, for only a few specific variables, and save the result to
individual CSV files.

More help on CGI parameters is available at:

    https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?help

You are free to use this however you want.

Author: daryl herzmann akrherz@iastate.edu
"""

import os
from datetime import date, datetime, timedelta

import requests


def fetch(station_id):
    """Download data we are interested in!"""
    localfn = f"{station_id}.csv"
    if os.path.isfile(localfn):
        print(f"- Cowardly refusing to over-write existing file: {localfn}")
        return
    print(f"+ Downloading for {station_id}")
    enddt = date.today() + timedelta(days=2)
    uri = (
        "http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
        f"station={station_id}&data=tmpc&year1=1928&month1=1&day1=1&"
        f"year2={enddt.year}&month2={enddt.month}&day2={enddt.day}&"
        "tz=Etc%2FUTC&format=onlycomma&latlon=no&elev=no&missing=M&trace=T&"
        "direct=yes&report_type=3"
    )
    res = requests.get(uri, timeout=300)
    with open(localfn, "w", encoding="utf-8") as fh:
        fh.write(res.text)


def main():
    """Main loop."""
    # Step 1: Fetch global METAR geojson metadata
    # https://mesonet.agron.iastate.edu/sites/networks.php
    req = requests.get(
        "http://mesonet.agron.iastate.edu/geojson/network/AZOS.geojson",
        timeout=60,
    )
    geojson = req.json()
    for feature in geojson["features"]:
        station_id = feature["id"]
        props = feature["properties"]
        # We want stations with data to today (archive_end is null)
        if props["archive_end"] is not None:
            continue
        # We want stations with data to at least 1943
        if props["archive_begin"] is None:
            continue
        archive_begin = datetime.strptime(props["archive_begin"], "%Y-%m-%d")
        if archive_begin.year > 1943:
            continue
        # Horray, fetch data
        fetch(station_id)


if __name__ == "__main__":
    main()
