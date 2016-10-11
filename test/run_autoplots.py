"""Attempt to call each autoplot and whine about API calls that error"""
import requests
import datetime
import pandas as pd


def get_formats(i):
    """Figure out which formats this script supports"""
    uri = "http://iem.local/plotting/auto/meta/%s.json" % (i, )
    res = requests.get(uri)
    if res.status_code == 404:
        print("%s resulted in 404, exiting..." % (i, ))
        return False
    if res.status_code != 200:
        print("%s. %s -> HTTP: %s" % (i, uri, res.status_code))
        print(res.text)
        return
    try:
        json = res.json()
    except:
        print("%s %s -> json failed" % (i, res.content))
        return
    fmts = ['png', ]
    if 'report' in json and json['report']:
        fmts.append('txt')
    if 'highcharts' in json and json['highcharts']:
        fmts.append('js')
    if json.get('data', False):
        fmts.append('csv')
        fmts.append('xlsx')
    return fmts


def run_plot(i, fmt):
    """Run this plot"""
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
        fmts = get_formats(i)
        if not fmts:
            break
        for fmt in fmts:
            sts = datetime.datetime.now()
            res = run_plot(i, fmt)
            if not res:
                break
            ets = datetime.datetime.now()
            timing.append({'i': i, 'fmt': fmt,
                           'secs': (ets - sts).total_seconds()})
        i += 1
    if len(timing) == 0:
        print("WARNING: no timing results found!")
        return
    df = pd.DataFrame(timing)
    df.set_index('i', inplace=True)
    df.sort_values('secs', ascending=False, inplace=True)
    print df.head(5)

if __name__ == '__main__':
    main()
