"""Attempt to call each autoplot and whine about API calls that error"""
from __future__ import print_function
import datetime
import sys

import requests
import pandas as pd


def get_formats(i):
    """Figure out which formats this script supports"""
    uri = "http://iem.local/plotting/auto/meta/%s.json" % (i, )
    try:
        res = requests.get(uri, timeout=10)
    except requests.exceptions.ReadTimeout:
        print("%s. %s -> Read Timeout" % (i, uri[16:]))
        sys.exit(1)
    if res.status_code == 404:
        print("%s resulted in 404, exiting..." % (i, ))
        return False
    if res.status_code != 200:
        print("%s. %s -> HTTP: %s" % (i, uri, res.status_code))
        print(res.text)
        return
    try:
        json = res.json()
    except Exception as exp:
        print("%s %s -> json failed\n%s" % (i, res.content, exp))
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
    uri = "http://iem.local/plotting/auto/plot/%s/dpi:100::_cb:1.%s" % (i, fmt)
    try:
        res = requests.get(uri, timeout=600)
    except requests.exceptions.ReadTimeout:
        print("%s. %s -> Read Timeout" % (i, uri[16:]))
        sys.exit(1)
    if res.status_code != 200 or len(res.content) == 0:
        print("%s. %s -> HTTP: %s len(content): %s" % (i, uri[16:],
                                                       res.status_code,
                                                       len(res.content)))
        if len(res.content) > 0 and fmt not in ['svg', 'png', 'pdf']:
            print(res.text)
        return False
    if res.status_code == 504:
        print("%s. %s -> HTTP: %s (timeout)" % (i, uri, res.status_code))
        return

    return True


def main():
    """Do Something"""
    timing = []
    i = 0  # autoplot starts at app 1 and not 0
    while True:
        i += 1
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
    if not timing:
        print("WARNING: no timing results found!")
        return
    df = pd.DataFrame(timing)
    df.set_index('i', inplace=True)
    df.sort_values('secs', ascending=False, inplace=True)
    print(df.head(5))


if __name__ == '__main__':
    main()
