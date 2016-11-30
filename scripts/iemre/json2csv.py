import requests
import pandas as pd


def do(gid, lat, lon):
    res = []
    for year in range(2010, 2016):
        print gid, year
        uri = ("http://mesonet.agron.iastate.edu/iemre/multiday/"
               "%s-01-01/%s-12-31/%s/%s/json"
               ) % (year, year, lat, lon)
        r = requests.get(uri)
        for row in r.json()['data']:
            res.append(row)
    df = pd.DataFrame(res)
    df.to_csv("%s.csv" % (gid,), index=False)


def main():
    for line in open('/tmp/pixlocation.txt'):
        (gid, lat, lon) = line.split()
        do(gid, lat, lon)

if __name__ == '__main__':
    main()
