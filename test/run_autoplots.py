"""Attempt to call each autoplot and whine about API calls that error"""
import requests
import datetime
import pandas as pd


def run_plot(i):
    """Run this plot"""
    uri = "http://iem.local/plotting/auto/meta/%s.json" % (i, )
    res = requests.get(uri)
    if res.status_code == 404:
        print("%s resulted in 404, exiting..." % (i, ))
        return False
    if res.status_code != 200:
        print("%s. %s -> HTTP: %s" % (i, uri, res.status_code))
        print(res.text)
        return
    json = res.json()
    fmts = ['png', ]
    if 'report' in json and json['report']:
        fmts.append('txt')
    if 'highcharts' in json and json['highcharts']:
        fmts.append('js')
    for fmt in fmts:
        uri = "http://iem.local/plotting/auto/plot/%s/dpi:100.%s" % (i, fmt)
        res = requests.get(uri)
        if res.status_code != 200:
            print("%s. %s -> HTTP: %s" % (i, uri, res.status_code))
            print(res.text)
            return False

    return True


def main():
    """Do Something"""
    timing = []
    i = 1  # autoplot starts at app 1 and not 0
    while True:
        sts = datetime.datetime.now()
        if not run_plot(i):
            break
        ets = datetime.datetime.now()
        timing.append({'i': i, 'secs': (ets - sts).total_seconds()})
        i += 1
    df = pd.DataFrame(timing)
    df.set_index('i', inplace=True)
    df.sort_values('secs', ascending=False, inplace=True)
    print df.head(5)

if __name__ == '__main__':
    main()
