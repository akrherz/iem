"""A util script to dump IEMRE json service to csv files"""
from __future__ import print_function

import requests
import pandas as pd


def workflow(gid, lat, lon):
    """Do Some Work Please"""
    res = []
    for year in range(2010, 2016):
        print("Processing GID: %s year: %s" % (gid, year))
        uri = ("http://mesonet.agron.iastate.edu/iemre/multiday/"
               "%s-01-01/%s-12-31/%s/%s/json"
               ) % (year, year, lat, lon)
        req = requests.get(uri)
        for row in req.json()['data']:
            res.append(row)
    df = pd.DataFrame(res)
    df.to_csv("%s.csv" % (gid,), index=False)


def main():
    """Go Main Go"""
    for line in open('/tmp/pixlocation.txt'):
        (gid, lat, lon) = line.split()
        workflow(gid, lat, lon)


if __name__ == '__main__':
    main()
